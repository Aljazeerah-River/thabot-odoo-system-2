from typing import Dict, List
from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_VERSION: str = "2.1.1-hardened"
    GCP_PROJECT: str = "thabot"
    SERVICE_URL: str = ""  # optional explicit audience for ID-token verification
    # Trust claims of tokens Cloud Run already validated (signature stripped by Google).
    # Requires --invoker-iam-check to stay enabled on the service.
    TRUST_CLOUD_RUN_IAM: bool = True
    # Extra accepted token audiences besides this service's own URL.
    # 32555940559.apps.googleusercontent.com = gcloud CLI (human admins using
    # `gcloud auth print-identity-token`). Remove it to allow service-to-service calls only.
    ALLOWED_AUDIENCES: List[str] = ["32555940559.apps.googleusercontent.com"]

    ODOO_URL: str = Field(default="", validation_alias=AliasChoices("ODOO_URL", "ODOO_BASE_URL"))
    ODOO_DB: str = Field(default="", validation_alias=AliasChoices("ODOO_DB", "ODOO_DB_NAME"))
    ODOO_USER: str = ""
    ODOO_PASSWORD: SecretStr = Field(default=SecretStr(""), validation_alias=AliasChoices("ODOO_PASSWORD", "ODOO_API_KEY"))
    XMLRPC_TIMEOUT_SECONDS: int = Field(default=15, ge=3, le=60)

    # Override via env var as JSON. Unknown callers get NO access (fail closed).
    GOVERNANCE_ADMINS: List[str] = [
        "asem.alkahtani@aljazeerahriver.com",
        "dr.asem@thabot.com",
        "sa-thabot@thabot.iam.gserviceaccount.com",
    ]
    ACTOR_ALLOWED_COMPANIES: Dict[str, List[int]] = {
        "asem.alkahtani@aljazeerahriver.com": [1, 2, 3, 4, 5, 6],
        "dr.asem@thabot.com": [1, 2, 3, 4, 5, 6],
        "sa-thabot@thabot.iam.gserviceaccount.com": [1],
    }


settings = Settings()
