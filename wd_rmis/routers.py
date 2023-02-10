from fastapi import APIRouter

api = APIRouter(
    prefix="/api/user",
    tags=['main_api_group'],
    responses={404: {"description": "Страница не найдена"}},
)

users_router = APIRouter(
    prefix="/user",
    responses={404: {"description": "Страница не найдена"}},
)

api.include_router(users_router)
