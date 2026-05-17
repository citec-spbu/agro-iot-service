from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class DatabaseSettings(BaseSettings):
    ECHO: bool = False

    USER: str
    PASSWORD: str
    HOST: str
    PORT: str
    DB: str

    @property
    def connection_string(self) -> str:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.USER,
            password=self.PASSWORD,
            host=self.HOST,
            port=int(self.PORT),
            database=self.DB,
        ).render_as_string(hide_password=False)

    model_config = SettingsConfigDict(
        env_prefix="POSTGRES_", env_file=".env", extra="ignore"
    )


db_settings = DatabaseSettings()
