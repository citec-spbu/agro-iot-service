from zoneinfo import ZoneInfo

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DEBUG: bool = False
    TITLE: str = "agro-iot-service"
    VERSION: str = "0.1.0"

    TZ_NAME: str = "Europe/Moscow"

    TCP_HOST: str = "0.0.0.0"
    TCP_PORT: int = 9000

    AUTH_SERVICE_URL: str = "http://auth-service:8080"
    GATEWAY_URL: str = "http://api-gateway:8080"

    ONLINE_THRESHOLD_SECONDS: int = 3600

    model_config = SettingsConfigDict(
        env_prefix="APP_", env_file=".env", extra="ignore"
    )

    @property
    def TZ(self) -> ZoneInfo:
        return ZoneInfo(self.TZ_NAME)


settings = Settings()
