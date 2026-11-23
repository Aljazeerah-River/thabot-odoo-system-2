# Thabot Odoo Bridge 2.1.1-hardened — deployment record (2026-10-27)

Live revisions (100% traffic, tag `hardened`):
- prod-odoo-thabot-bridge-00008-gos
- dev-odoo-thabot-bridge-00015-bad

Image (OCI index digest):
me-central2-docker.pkg.dev/thabot/odoo-thabot-bridge-repo/dev-odoo-thabot-bridge@sha256:b4f109269fa249e8c8e90207828977f7aa5429ca4eb63034a5e5930031f2259a

Required runtime configuration (in addition to existing ODOO_URL / ODOO_DB / ODOO_USER and
secret ODOO_PASSWORD=thabot-odoo-api-key:1):
- ALLOWED_AUDIENCES = ["32555940559.apps.googleusercontent.com",
  "618104708054-9r9s1c4alg36erliucho9t52n32n6dgq.apps.googleusercontent.com"]
  (gcloud CLI and Cloud Shell OAuth clients, for human governance admins)
  gcloud form: --update-env-vars='^@^ALLOWED_AUDIENCES=[...]'

Security preconditions:
- Cloud Run Invoker IAM check MUST stay enabled and no allUsers/allAuthenticatedUsers binding
  (tokens with SIGNATURE_REMOVED_BY_GOOGLE are trusted only because Cloud Run verified them).
- sa-thabot needs roles/datastore.user; until then the kill-switch state is unreadable and
  write tools are blocked (fail-closed).

Rollback revisions: prod-odoo-thabot-bridge-00004-c44, dev-odoo-thabot-bridge-00005-ps2 (pre-hardening code).

Tests: tests/test_app.py, tests/test_auth.py (32 checks; run from the folder containing app/).
