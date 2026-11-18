import sys, json, base64, time, asyncio
sys.path.insert(0, "app")
import governance.kill_switch as ks
ks.get_kill_switch_state = lambda: {"killed": False}
import api.governance as g
g.get_kill_switch_state = lambda: {"killed": False}
from api.governance import caller_claims, verified_email
def tok(claims, sig="SIGNATURE_REMOVED_BY_GOOGLE"):
    b = lambda d: base64.urlsafe_b64encode(json.dumps(d).encode()).decode().rstrip("=")
    return "bearer " + b({"alg":"RS256"}) + "." + b(claims) + "." + sig
ok = {"iss":"https://accounts.google.com","email":"asem.alkahtani@aljazeerahriver.com","email_verified":True,"exp":time.time()+600,"aud":"32555940559.apps.googleusercontent.com"}
print("A stripped valid ->", verified_email(tok(ok)))
print("B expired ->", repr(verified_email(tok({**ok,"exp":time.time()-5}))))
print("C wrong iss ->", repr(verified_email(tok({**ok,"iss":"evil"}))))
print("D unverified email ->", repr(verified_email(tok({**ok,"email_verified":False}))))
print("E forged real sig ->", repr(verified_email(tok(ok, sig="abc"))))
print("F no bearer ->", repr(verified_email("Basic x")))
import os
print("K wrong aud ->", repr(verified_email(tok({**ok,"aud":"https://other-service-xyz.a.run.app"}))))
print("L no aud ->", repr(verified_email(tok({k:v for k,v in ok.items() if k!="aud"}))))
os.environ["K_SERVICE"]="prod-odoo-thabot-bridge"
print("M own service aud ->", repr(verified_email(tok({**ok,"aud":"https://prod-odoo-thabot-bridge-221375339753.me-central2.run.app"}))))
print("N sibling service aud ->", repr(verified_email(tok({**ok,"aud":"https://dev-odoo-thabot-bridge-221375339753.me-central2.run.app"}))))
g.settings.TRUST_CLOUD_RUN_IAM = False
print("G trust disabled ->", repr(verified_email(tok(ok))))
g.settings.TRUST_CLOUD_RUN_IAM = True
import httpx, main
async def t():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=main.app), base_url="http://t") as c:
        print("H status admin", (await c.get("/api/v1/governance/status", headers={"authorization": tok(ok)})).status_code)
        print("I status non-admin", (await c.get("/api/v1/governance/status", headers={"authorization": tok({**ok,"email":"x@y.com"})})).status_code)
        print("J status none", (await c.get("/api/v1/governance/status")).status_code)
asyncio.run(t())
