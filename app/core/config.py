from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Adrobot"
    app_env: str = "development"
    app_debug: bool = True

    database_url: str = "sqlite:///./adrobot.db"

    keitaro_base_url: str = "https://tlgk.host"
    keitaro_api_key: str = ""

    keitaro_domain_id: int = 1813
    keitaro_group_id: int = 10332
    keitaro_traffic_source_id: int = 836

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
