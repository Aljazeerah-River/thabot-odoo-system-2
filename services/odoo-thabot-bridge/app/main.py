import asyncio
import contextvars
import hashlib
import json
import logging
import time
import uuid
import xmlrpc.client
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from google.api_core.exceptions import AlreadyExists
from mcp.server.fastmcp import FastMCP
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from api.governance import router as governance_router
from api.governance import verified_email
from config import settings
from governance.kill_switch import check_kill_switch, get_firestore_client


# 1. Logging: structured, no recursion, no raw headers/bodies
class CloudLoggingFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "severity": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "timestamp": self.formatTime(record),
        }
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry, ensure_ascii=False)


_handler = logging.StreamHandler()
_handler.setFormatter(CloudLoggingFormatter())
for _name in ("odoo-mcp-bridge", "thabot.governance"):
    _lg = logging.getLogger(_name)
    _lg.handlers = [_handler]
    _lg.setLevel(logging.INFO)
    _lg.propagate = False
logger = logging.getLogger("odoo-mcp-bridge")

caller_email_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("caller_email", default="")


# 2. Whitelist of models/fields + server-side company isolation
ALLOWED_MODELS_FIELDS: Dict[str, set] = {
    "product.product": {"id", "display_name", "default_code", "barcode", "uom_id", "qty_available", "company_id"},
    "product.template": {"id", "display_name", "name", "categ_id", "list_price", "standard_price", "company_id"},
    "stock.quant": {"id", "product_id", "location_id", "quantity", "reserved_quantity", "company_id"},
    "stock.picking": {"id", "name", "state", "location_id", "location_dest_id", "scheduled_date", "company_id"},
    "stock.scrap": {"id", "name", "product_id", "scrap_qty", "state", "date_done", "company_id"},
    "mrp.production": {"id", "name", "product_id", "product_qty", "state", "date_start", "company_id"},
    "mrp.bom": {"id", "display_name", "product_tmpl_id", "product_qty", "company_id"},
    "sale.order": {"id", "name", "partner_id", "amount_total", "state", "date_order", "company_id"},
    "purchase.order": {"id", "name", "partner_id", "amount_total", "state", "date_order", "company_id"},
    "res.partner": {"id", "display_name", "name", "email", "phone", "city", "company_id"},
    "fleet.vehicle": {"id", "name", "license_plate", "driver_id", "odometer", "company_id"},
}
ALLOWED_OPERATORS = {"=", "!=", ">", ">=", "<", "<=", "in", "not in", "ilike", "like"}


def get_caller_allowed_companies() -> List[int]:
    # Fail closed: an unknown or unverified caller gets no company at all.
    return settings.ACTOR_ALLOWED_COMPANIES.get(caller_email_ctx.get(), [])


def sanitize_and_validate_query(model: str, domain: Optional[list], fields: Optional[list], limit: int):
    if model not in ALLOWED_MODELS_FIELDS:
        raise ValueError(f"Model '{model}' is not in the approved whitelist.")
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
        raise ValueError("Parameter 'limit' must be an integer between 1 and 100.")
    allowed_fields = ALLOWED_MODELS_FIELDS[model]
    safe_fields = list(fields) if fields else ["display_name"]
    for f in safe_fields:
        if not isinstance(f, str) or f not in allowed_fields:
            raise ValueError(f"Field '{f}' is not permitted on model '{model}'.")
    safe_domain: list = []
    if domain:
        if not isinstance(domain, list) or len(domain) > 20:
            raise ValueError("Invalid domain format or length.")
        for cond in domain:
            if not (isinstance(cond, (list, tuple)) and len(cond) == 3):
                raise ValueError("Only standard 3-element domain conditions are permitted.")
            field_name, op, val = cond
            if field_name not in allowed_fields or op not in ALLOWED_OPERATORS:
                raise ValueError(f"Disallowed filter condition on '{field_name}'.")
            if field_name == "company_id":
                continue  # company scope is enforced by the server only
            safe_domain.append([field_name, op, val])
    companies = get_caller_allowed_companies()
    if not companies:
        raise PermissionError("Caller is not authorized for any company.")
    # Records shared across companies have company_id = False in Odoo.
    safe_domain += ["|", ["company_id", "=", False], ["company_id", "in", companies]]
    return safe_domain, safe_fields


# 3. Odoo XML-RPC with timeout + retry
class TimeoutTransport(xmlrpc.client.Transport):
    def __init__(self, timeout: int, use_https: bool):
        super().__init__()
        self.timeout, self.use_https = timeout, use_https

    def make_connection(self, host):
        import http.client
        real_host = host[0] if isinstance(host, tuple) else host
        cls = http.client.HTTPSConnection if self.use_https else http.client.HTTPConnection
        return cls(real_host, timeout=self.timeout)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
    retry=retry_if_exception_type((OSError, ConnectionError)),
    reraise=True,
)
def execute_odoo_kw(model: str, method: str, args: list, kwargs: dict) -> Any:
    if not settings.ODOO_URL:
        raise RuntimeError("Odoo URL is not configured.")
    base = settings.ODOO_URL.rstrip("/")
    transport = TimeoutTransport(settings.XMLRPC_TIMEOUT_SECONDS, base.startswith("https"))
    password = settings.ODOO_PASSWORD.get_secret_value()
    common = xmlrpc.client.ServerProxy(f"{base}/xmlrpc/2/common", transport=transport, allow_none=True)
    uid = common.authenticate(settings.ODOO_DB, settings.ODOO_USER, password, {})
    if not uid:
        raise RuntimeError("Odoo authentication failed.")
    obj = xmlrpc.client.ServerProxy(f"{base}/xmlrpc/2/object", transport=transport, allow_none=True)
    return obj.execute_kw(settings.ODOO_DB, uid, password, model, method, args, kwargs)


# 4. MCP server and tools (query_odoo kept for client compatibility)
mcp_server = FastMCP(
    name="Odoo Enterprise Bridge",
    instructions=(
        "This server connects to the Odoo ERP system. Use query_odoo to read whitelisted business "
        "records (products, stock, manufacturing, sales, purchases, partners, fleet)."
    ),
    stateless_http=True,
    json_response=True,
)


@mcp_server.tool(
    name="query_odoo",
    description="Query whitelisted Odoo models (read-only) with server-enforced company isolation. limit 1-100.",
)
@check_kill_switch
async def query_odoo(
    model: str,
    domain: Optional[List[List[Any]]] = None,
    fields: Optional[List[str]] = None,
    limit: int = 10,
) -> Dict[str, Any]:
    try:
        safe_domain, safe_fields = sanitize_and_validate_query(model, domain, fields, limit)
    except (ValueError, PermissionError) as e:
        return {"status": "error", "error": str(e)}
    try:
        records = await asyncio.to_thread(
            execute_odoo_kw, model, "search_read", [safe_domain], {"fields": safe_fields, "limit": limit}
        )
        return {"status": "success", "model": model, "count": len(records), "records": records}
    except Exception:
        logger.error("Odoo query failed for model %s", model, exc_info=True)
        return {"status": "error", "error": "Upstream ERP query failed."}


def _create_waste_draft(lock_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    ref = get_firestore_client().collection("thabot_waste_drafts").document(lock_id)
    try:
        ref.create(data)
        return {"status": "success", "idempotent_replay": False, "draft_id": lock_id, "state": "draft"}
    except AlreadyExists:
        existing = ref.get().to_dict() or {}
        if existing.get("payload_hash") != data["payload_hash"]:
            return {"status": "error", "error": "Idempotency key conflict with different payload."}
        return {"status": "success", "idempotent_replay": True, "draft_id": lock_id, "state": existing.get("state", "draft")}


@mcp_server.tool(
    name="propose_waste_draft",
    description="Record an idempotent waste draft awaiting supervisor approval. Does not touch Odoo inventory.",
)
@check_kill_switch(fail_closed=True)
async def propose_waste_draft(
    external_event_id: str,
    product_id: int,
    quantity: float,
    reason: str,
    company_id: int,
) -> Dict[str, Any]:
    if company_id not in get_caller_allowed_companies():
        return {"status": "error", "error": "Unauthorized company_id for caller."}
    event_id, reason = external_event_id.strip(), reason.strip()
    if not 4 <= len(event_id) <= 64 or not 0 < quantity <= 10000 or not 3 <= len(reason) <= 255:
        return {"status": "error", "error": "Invalid event id, quantity or reason."}
    payload_hash = hashlib.sha256(f"{company_id}:{product_id}:{quantity}:{reason}".encode()).hexdigest()
    lock_id = hashlib.sha256(f"{company_id}:waste_draft:{event_id}".encode()).hexdigest()
    data = {
        "external_event_id": event_id, "company_id": company_id, "product_id": product_id,
        "quantity": quantity, "reason": reason, "state": "draft", "payload_hash": payload_hash,
        "caller": caller_email_ctx.get(), "created_at": int(time.time()),
    }
    try:
        return await asyncio.to_thread(_create_waste_draft, lock_id, data)
    except Exception:
        logger.error("Failed to create waste draft", exc_info=True)
        return {"status": "error", "error": "Internal storage error while recording waste draft."}


# 5. FastAPI app + hardened middleware
mcp_app = mcp_server.streamable_http_app()
mcp_app.router.redirect_slashes = False  # Gemini's client does not follow 307


@asynccontextmanager
async def lifespan(app: FastAPI):
    # REQUIRED: starts the MCP session manager task group (mounted apps get no lifespan).
    logger.info("Starting Odoo MCP Bridge %s", settings.APP_VERSION)
    async with mcp_app.router.lifespan_context(app):
        yield
    logger.info("Shutting down Odoo MCP Bridge")


app = FastAPI(
    title="Thabot Odoo Enterprise Bridge",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
MAX_BODY_BYTES = 256 * 1024
_verified_email = verified_email  # shared with governance endpoints


@app.middleware("http")
async def hardened_middleware(request: Request, call_next):
    req_id = str(uuid.uuid4())
    start = time.time()
    try:
        too_big = int(request.headers.get("content-length") or 0) > MAX_BODY_BYTES
    except ValueError:
        too_big = True
    if too_big:
        return JSONResponse(status_code=413, content={"detail": "Payload too large."})
    if request.scope.get("path") == "/mcp":
        request.scope["path"] = "/mcp/"
        request.scope["raw_path"] = b"/mcp/"
    email = ""
    if request.scope["path"].startswith("/mcp"):
        email = await asyncio.to_thread(_verified_email, request.headers.get("authorization", ""))
    token = caller_email_ctx.set(email)
    try:
        response = await call_next(request)
    finally:
        caller_email_ctx.reset(token)
    logger.info(json.dumps({
        "event": "http_request", "req_id": req_id, "method": request.method,
        "path": request.scope.get("path"), "caller": email or "unverified",
        "status": response.status_code, "latency_ms": round((time.time() - start) * 1000, 1),
    }))
    response.headers["X-Request-ID"] = req_id
    return response


@app.get("/health")
def health():
    return {"status": "online", "system": "odoo-bridge", "version": settings.APP_VERSION}


app.include_router(governance_router)
app.mount("/", mcp_app)
