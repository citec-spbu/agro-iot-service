from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    ECHO: bool = False

    USER: str
    PASSWORD: str
    HOST: str
    PORT: str
    DB: str

    @property
    def connection_string(self) -> str:
        return (
            f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@"
            f"{self.HOST}:{self.PORT}/{self.DB}"
        )

    model_config = SettingsConfigDict(
        env_prefix="POSTGRES_", env_file=".env", extra="ignore"
    )


db_settings = DatabaseSettings()
