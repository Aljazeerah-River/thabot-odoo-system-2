import base64
import json
import os
import time
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from pydantic import BaseModel, Field

from config import settings
from governance.kill_switch import activate_kill_switch, get_kill_switch_state, reset_kill_switch

router = APIRouter(prefix="/api/v1/governance", tags=["governance"])
TRUSTED_ISSUERS = {"accounts.google.com", "https://accounts.google.com"}
CLOUD_RUN_STRIPPED_SIGNATURE = "SIGNATURE_REMOVED_BY_GOOGLE"
_google_request = google_requests.Request()


def audience_allowed(aud: Any) -> bool:
    """aud must be this service's own URL (service-to-service calls) or an explicitly allowed
    client ID (e.g. gcloud CLI for human admins). Blocks replay of tokens minted for other services."""
    if not isinstance(aud, str) or not aud:
        return False
    if aud in settings.ALLOWED_AUDIENCES or (settings.SERVICE_URL and aud == settings.SERVICE_URL.rstrip("/")):
        return True
    service = os.environ.get("K_SERVICE", "")  # set by Cloud Run
    return bool(service) and aud.startswith(f"https://{service}-") and aud.rstrip("/").endswith(".run.app")


def caller_claims(auth_header: str) -> Dict[str, Any]:
    """Return verified ID-token claims, or {} when the caller cannot be identified."""
    if auth_header[:7].lower() != "bearer ":
        return {}
    token = auth_header[7:].strip()
    parts = token.split(".")
    if len(parts) != 3:
        return {}
    if parts[2] == CLOUD_RUN_STRIPPED_SIGNATURE:
        # Cloud Run already validated this token (Invoker IAM check) and stripped its signature.
        # Safe ONLY while the service keeps --invoker-iam-check enabled and has no allUsers binding.
        if not settings.TRUST_CLOUD_RUN_IAM:
            return {}
        try:
            claims = json.loads(base64.urlsafe_b64decode(parts[1] + "=" * (-len(parts[1]) % 4)))
        except Exception:
            return {}
        if claims.get("iss") not in TRUSTED_ISSUERS or float(claims.get("exp", 0)) < time.time():
            return {}
    else:
        try:
            claims = id_token.verify_oauth2_token(token, _google_request, audience=None)
        except Exception:
            return {}
    return claims if audience_allowed(claims.get("aud")) else {}


def verified_email(auth_header: str) -> str:
    claims = caller_claims(auth_header)
    return claims.get("email", "") if claims.get("email_verified") else ""


class KillRequest(BaseModel):
    reason: str = Field(default="Emergency manual halt", min_length=3, max_length=255)


def verify_governance_admin(request: Request) -> str:
    email = verified_email(request.headers.get("authorization", ""))
    if not email:
        raise HTTPException(status_code=401, detail="Missing or invalid Google ID token.")
    if email not in settings.GOVERNANCE_ADMINS:
        raise HTTPException(status_code=403, detail="Caller is not an authorized governance admin.")
    return email


@router.get("/status")
def status_endpoint(admin: str = Depends(verify_governance_admin)):
    return get_kill_switch_state()


@router.post("/kill")
def kill_endpoint(req: KillRequest, admin: str = Depends(verify_governance_admin)):
    return activate_kill_switch(actor_email=admin, reason=req.reason)


@router.post("/reset")
def reset_endpoint(admin: str = Depends(verify_governance_admin)):
    return reset_kill_switch(actor_email=admin)
