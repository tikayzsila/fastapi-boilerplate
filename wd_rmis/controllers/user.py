from fastapi import Depends, HTTPException, status, APIRouter
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from ..schemas.user import CreateUser, User, GetAllUsers
from ..schemas.token import Token
from ..schemas.message import Message
from ..models.user import DBUser
from ..utils import jwt as j

users_router = APIRouter(
    prefix="/user",
    tags=['users api'],
    responses={404: {"description": "Страница не найдена"}},
)

@users_router.post("/registration", response_model=User, responses={404: {"model":Message},
                                                          409: {"model":Message}
                                                          })
async def create_user(*, user: CreateUser) -> CreateUser:
    # добавить проверку роли
    passwd = j.get_password_hash(user.password)
    check_login = await DBUser.objects.get_or_none(login=user.login)

    if check_login != None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                detail=f"Пользователь с логином {check_login.login} уже существует")
    
    q = await DBUser.objects.create(login=user.login, fio=user.fio, password=passwd, role=user.role)
    
    user_data = User(
        user_id=q.user_id,
        login=user.login,
        fio=user.fio,
        role=user.role,
    )
    
    return user_data
