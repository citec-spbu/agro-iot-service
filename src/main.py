import json
import logging
import logging.config
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from src.api import router as iot_router
from src.config import settings
from src.tcp_server import start_tcp_server

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    with Path("logs_config.json").open("r") as f:
        config = json.load(f)
    logging.config.dictConfig(config)


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    setup_logging()
    tcp_server = await start_tcp_server(settings.TCP_HOST, settings.TCP_PORT)
    logger.info("Application startup complete.")
    yield
    tcp_server.close()
    await tcp_server.wait_closed()
    logger.info("Application shutdown complete.")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.TITLE,
        version=settings.VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )
    app.include_router(iot_router)
    return app
