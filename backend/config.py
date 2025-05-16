from pydantic_settings import BaseSettings
from pydantic import ConfigDict, BaseModel
from functools import lru_cache
from yaml import safe_load
from dotenv import load_dotenv
import os
from .models import RSS_Journal
import logging

# no level is specified, to prevent circular import
logger = logging.getLogger(__name__)

# config
# ===========================
class LLM_Config(BaseModel):
    base_url: str
    api_key: str
    model_name: str
    prompt: str
    model_args: dict = {}

    @classmethod
    def mock(cls):
        return cls(
            base_url="",
            api_key="",
            model_name="",
            prompt="",
        )
    

class ADMIN_Config(BaseModel):
    username: str = 'admin'
    realm: str = "admin-panel"
    token: str = ''


class AppSettings(BaseSettings):
    """
    App settings
    """
    LLM_API: LLM_Config = LLM_Config.mock()
    ADMIN_PANEL: ADMIN_Config = ADMIN_Config()

    SQLITE_URL: str = "sqlite:///database.db"
    RSS_SCHEMA_YML: str = "backend/config/rss.yml"
    DEBUG: bool = False

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    BASE_URL: str = "/"

    RSS_JOURNALS: dict[str, RSS_Journal] = {}

    model_config = ConfigDict(
        extra="allow",
    )


@lru_cache
def get_config():
    if os.path.isfile(".env"):
        load_dotenv(".env")

    app_config_path = os.getenv("APP_CONFIG_PATH", "backend/config/default.yml")
    default_config_path = "backend/config/default.yml"
    # fallback to default config if dev config not exist
    if not os.path.isfile(app_config_path):
        if not os.path.isfile(default_config_path):
            raise FileNotFoundError(
                f"Config file not found: {app_config_path}. Please create a config file."
            )
        logger.warning(
            f"Config file not found: {app_config_path}. Using default config: {default_config_path}."
        )
        app_config_path = "backend/config/default.yml"

    with open(app_config_path, "r", encoding="utf-8") as fp:
        app_config:dict = safe_load(fp.read())

    with open(
        app_config.get("RSS_SCHEMA_YML", "backend/rss/rss.yml"), "r", encoding="utf-8"
    ) as fp:
        rss_schema_raw = safe_load(fp.read())

    rss_schemas = {}
    for journal_key, journal_obj_raw in rss_schema_raw.items():
        rss_schemas[journal_key] = RSS_Journal.model_validate(
            journal_obj_raw
        ).model_dump()
    app_config["RSS_JOURNALS"] = rss_schemas

    app_config_model = AppSettings.model_validate(app_config)

    return app_config_model

