import asyncio, json, sys, logging
sys.path.insert(0, "app")
from google.api_core.exceptions import AlreadyExists
import governance.kill_switch as ks

class FakeDoc:
    def __init__(s, store, key): s.store, s.key = store, key
    def get(s):
        d = s.store.get(s.key); o = type("S", (), {})(); o.exists = d is not None; o.to_dict = lambda: d; return o
    def set(s, data): s.store[s.key] = dict(data)
    def create(s, data):
        if s.key in s.store: raise AlreadyExists("x")
        s.store[s.key] = dict(data)
class FakeFS:
    def __init__(s): s.store = {}
    def document(s, path): return FakeDoc(s.store, path)
    def collection(s, c): return type("C", (), {"document": lambda _, d: FakeDoc(s.store, c + "/" + d)})()
fs = FakeFS(); ks._client = fs
import main
main.get_firestore_client = lambda: fs
CALLS = []
def fake_odoo(model, method, args, kwargs):
    CALLS.append((model, args, kwargs)); return [{"id": 1, "display_name": "Bread"}]
main.execute_odoo_kw = fake_odoo
WHO = {"v": ""}
main._verified_email = lambda h: WHO["v"]
import httpx
H = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json"}
async def call(c, name, args):
    r = await c.post("/mcp", json={"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":name,"arguments":args}}, headers=H)
    res = r.json()["result"]; t = res["content"][0]["text"]
    return res.get("isError"), (json.loads(t) if t.startswith("{") else t)
async def main_t():
    async with main.app.router.lifespan_context(main.app):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=main.app), base_url="http://t") as c:
            print("1 health", (await c.get("/health")).json())
            r = await c.post("/mcp", json={"jsonrpc":"2.0","id":1,"method":"tools/list"}, headers=H)
            print("2 tools", [t["name"] for t in r.json()["result"]["tools"]])
            print("3 unknown caller", await call(c, "query_odoo", {"model":"product.product"}))
            WHO["v"] = "asem.alkahtani@aljazeerahriver.com"
            print("4 res.users", await call(c, "query_odoo", {"model":"res.users"}))
            print("5 limit 0", await call(c, "query_odoo", {"model":"product.product","limit":0}))
            print("6 bad field", await call(c, "query_odoo", {"model":"product.product","fields":["password"]}))
            print("7 ok", await call(c, "query_odoo", {"model":"product.product","fields":["id","display_name"],"limit":5,"domain":[["company_id","=",99],["default_code","ilike","GF"]]}))
            print("   domain sent:", CALLS[-1][1])
            a = {"external_event_id":"EVT-0001","product_id":7,"quantity":2.5,"reason":"burnt batch","company_id":2}
            print("8 waste", await call(c, "propose_waste_draft", a))
            print("9 replay", await call(c, "propose_waste_draft", a))
            print("10 conflict", await call(c, "propose_waste_draft", {**a, "quantity": 3}))
            print("11 other company", await call(c, "propose_waste_draft", {**a, "company_id": 9}))
            print("12 /kill no token", (await c.post("/api/v1/governance/kill", json={})).status_code)
            print("13 /reset no token", (await c.post("/api/v1/governance/reset")).status_code)
            fs.store["thabot_governance/kill_switch"] = {"killed": True}
            print("14 killed", await call(c, "query_odoo", {"model":"product.product"}))
            fs.store["thabot_governance/kill_switch"] = {"killed": False}
            real = ks.get_kill_switch_state
            ks.get_kill_switch_state = lambda: {"killed": False, "readable": False}
            print("17 unreadable read", await call(c, "query_odoo", {"model":"product.product"}))
            print("18 unreadable write", await call(c, "propose_waste_draft", {**a, "external_event_id":"EVT-0002"}))
            ks.get_kill_switch_state = real
            print("15 413", (await c.post("/mcp", content=b"x"*300000, headers=H)).status_code)
            print("16 /docs", (await c.get("/docs")).status_code)
    try:
        raise ValueError("boom")
    except ValueError:
        main.logger.error("formatter test", exc_info=True)
asyncio.run(main_t())
