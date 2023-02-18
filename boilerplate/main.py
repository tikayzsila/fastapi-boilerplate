from fastapi import FastAPI, APIRouter
import os, logging
from .utils.seed import seed_data
from .utils.db import database, conn_to_db
from .utils.log_conf import LogConfig
from .controllers.user import users_router
from .controllers.role import roles_router
from logging.config import dictConfig
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware

dictConfig(LogConfig().dict())
logger = logging.getLogger("default_logger")

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
    )
]


if os.environ.get("ENV") == 'prod':
    app = FastAPI(middleware=middleware, openapi_url=None, docs_url=None, redoc_url=None)
else:
    app = FastAPI(middleware=middleware)


api = APIRouter(
    prefix="/api",
    responses={404: {"description": "Страница не найдена"}},
)

api.include_router(users_router)
api.include_router(roles_router)
app.include_router(api)


@app.on_event("startup")
async def startup():
    if not database.is_connected:
        await conn_to_db()
        await database.connect()
        await seed_data('roles')
        await seed_data('users')


@app.on_event("shutdown")
async def shutdown():
    if database.is_connected:
        await database.disconnect()
