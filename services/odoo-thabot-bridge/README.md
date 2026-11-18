# Odoo Thabot Bridge — 2.1.1-hardened (B00 source import)

Provenance import of the live Cloud Run bridge source that was running in GCP project `thabot` (region `me-central2`) as revisions:

- `prod-odoo-thabot-bridge-00008-gos`
- `dev-odoo-thabot-bridge-00015-bad`

Image digest (OCI index):  
`me-central2-docker.pkg.dev/thabot/odoo-thabot-bridge-repo/dev-odoo-thabot-bridge@sha256:b4f109269fa249e8c8e90207828977f7aa5429ca4eb63034a5e5930031f2259a`  
Tag: `hardened-2-1-3`

## What this PR / folder is

- **B00 only:** put the hardened source into Git.
- **Not** a live Odoo connection proof.
- **Not** Workload Identity / GitHub→GCP deploy wiring.
- **No** deploy workflow is added here.

Canonical platform monorepo remains `Aljazeerah-River/thabot-core`. This folder is the verified package landing (and may be mirrored into `thabot-core` under the same path).

## Layout

```text
app/           # runtime sources (Dockerfile, main.py, governance, …)
tests/         # test_app.py, test_auth.py
DEPLOYMENT.md  # historical deploy record (2026-10-27)
SOURCE_PROVENANCE.md
```

## Run tests locally

```bash
cd services/odoo-thabot-bridge
python3 -m venv .venv
source .venv/bin/activate
pip install -r app/requirements.txt pytest httpx
# tests insert sys.path "app" relative to CWD
cd tests && PYTHONPATH=../app python3 test_auth.py
PYTHONPATH=../app python3 test_app.py
```

See `SOURCE_PROVENANCE.md` for package hashes and `docs/reports/THABOT_CLOUD_HANDOFF_2026-10-27_AR.md` for the historical handoff (evidence dated 2026-10-27, not a fresh live audit).
