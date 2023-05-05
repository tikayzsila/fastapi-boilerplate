from fastapi import FastAPI, APIRouter, Request
import os
import logging
from logging import config
from .utils.seed import seed_data
from .utils.db import database, wait_and_migrate
from .controllers.user import users_router
from fastapi.middleware import Middleware, cors

config.fileConfig(f"{os.getcwd()}/logger.conf", disable_existing_loggers=False)
log = logging.getLogger(__name__)

middleware = [
    Middleware(
        cors.CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
]

if os.environ.get("ENV") == "prod":
    app = FastAPI(middleware=middleware, openapi_url=None, docs_url=None, redoc_url=None)
else:
    app = FastAPI(
        middleware=middleware,
        openapi_url="/api/openapi.json",
        docs_url="/api/docs",
    )


@app.middleware("http")
# type: ignore
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    logging.info(
        f"HTTP Request - {request.method} {request.url.path} - "
        f"HTTP Response - {response.status_code} "
        f"Client IP - {request.client.host}\n"
        f"Request {request.headers}"
    )
    return response


api = APIRouter(
    prefix="/api",
    responses={404: {"description": "Страница не найдена"}},
)

api.include_router(users_router)
app.include_router(api)


@app.on_event("startup")
async def startup():
    if not database.is_connected:
        await wait_and_migrate()
        await database.connect()
        await seed_data("users")


@app.on_event("shutdown")
async def shutdown():
    if database.is_connected:
        await database.disconnect()
