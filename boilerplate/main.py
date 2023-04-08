from fastapi import FastAPI, APIRouter, Request
import os, logging, random, string, time
from .utils.seed import seed_data
from .utils.db import database, wait_and_migrate
from .controllers.user import users_router
from fastapi.middleware import Middleware, cors

logging.config.fileConfig(f'{os.getcwd()}/logger.conf', disable_existing_loggers=False)
log = logging.getLogger(__name__)

middleware = [
    Middleware(
        cors.CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
    )
]

if os.environ.get("ENV") == 'prod':
    app = FastAPI(
        middleware=middleware, 
        openapi_url=None, 
        docs_url=None, 
        redoc_url=None
    )
else:
    app = FastAPI(
        middleware=middleware,
        openapi_url="/api/openapi.json",
        docs_url="/api/docs",
    )

@app.middleware("http")
async def log_requests(request: Request, call_next):
    idem = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    log.info(f"rid={idem} start request path={request.url.path}")
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = '{0:.2f}'.format(process_time)
    log.info(f"rid={idem} completed_in={formatted_process_time}ms status_code={response.status_code}")
    
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
        await seed_data('users')


@app.on_event("shutdown")
async def shutdown():
    if database.is_connected:
        await database.disconnect()
