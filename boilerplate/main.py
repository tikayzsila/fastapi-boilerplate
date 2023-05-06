from fastapi import FastAPI, APIRouter, Request
import os
import logging
import time
import psutil
from typing import cast
from logging import config
from .utils.seed import seed_data
from .utils.db import database, migrate
from .controllers.user import users_router
from fastapi.middleware import Middleware, cors
from aioprometheus import Counter, MetricsMiddleware, REGISTRY, Summary, Gauge
from aioprometheus.asgi.starlette import metrics
from aioprometheus.pusher import Pusher

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
PUSH_GATEWAY_ADDR = "http://127.0.0.1:9091"
pusher = Pusher("my-job", PUSH_GATEWAY_ADDR, grouping_key={"instance": "test-app"})
app.state.users_events_counter = Counter("events", "Number of events.")
app.state.response_time = Summary("response_time", "Response time")
app.state.cpu_use = Gauge("CPU_USAGE", "CPU usage in %")
app.state.ram_use = Gauge("RAM_USAGE", "RAM usage in %")
app.add_middleware(MetricsMiddleware)
app.add_route("/metrics", metrics)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000

    request.app.state.users_events_counter.inc({"path": request.scope["path"]})
    request.app.state.response_time.observe({"lat": request.scope["path"]}, process_time)
    request.app.state.cpu_use.set({"type": "cpu %"}, psutil.cpu_percent())
    request.app.state.ram_use.set({"type": "ram %"}, psutil.virtual_memory().percent)

    client_ip = cast(str, request.client)
    logging.info(
        f"HTTP Request - {request.method} {request.url.path} - \n \
HTTP Response - {response.status_code} \n \
Client IP - {client_ip} \n \
Request {request.headers}"
    )
    await pusher.replace(REGISTRY)
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
        await database.connect()
        await migrate()
        await seed_data("users")


@app.on_event("shutdown")
async def shutdown():
    if database.is_connected:
        await database.disconnect()
