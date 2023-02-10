from fastapi import FastAPI, APIRouter
import os, logging
from wd_rmis.log_conf import LogConfig
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

@api.get("/home")
async def home_route():
    return {"message": "Hello World"}

app.include_router(router=api)