from fastapi import FastAPI, APIRouter
import os, logging
from wd_rmis.utils.db import database
from wd_rmis.utils.log_conf import LogConfig
from logging.config import dictConfig

dictConfig(LogConfig().dict())
logger = logging.getLogger("default_logger")
if os.environ.get("ENV") == 'prod':
    app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)
else:
    app = FastAPI()

api = APIRouter(
    prefix="/api",
    responses={404: {"description": "Страница не найдена"}},
)

@app.on_event("startup")
async def startup():
    if not database.is_connected:
        await database.connect()

@app.on_event("shutdown")
async def shutdown():
    if database.is_connected:
        await database.disconnect()


@api.get("/home")
async def home_route():
    return {"message": "Hello World"}

app.include_router(router=api)