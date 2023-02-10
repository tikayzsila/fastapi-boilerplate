from fastapi import FastAPI, APIRouter
import os, logging
from .utils.db import database
from .utils.log_conf import LogConfig
from .controllers.user import users_router
from logging.config import dictConfig


dictConfig(LogConfig().dict())
logger = logging.getLogger("default_logger")
if os.environ.get("ENV") == 'prod':
    app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)
else:
    app = FastAPI()


api = APIRouter(
    prefix="/api",
    tags=['all api'],
    responses={404: {"description": "Страница не найдена"}},
)

api.include_router(users_router)
app.include_router(api)

@app.on_event("startup")
async def startup():
    if not database.is_connected:
        await database.connect()

@app.on_event("shutdown")
async def shutdown():
    if database.is_connected:
        await database.disconnect()
