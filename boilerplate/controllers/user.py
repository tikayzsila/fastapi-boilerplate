from fastapi import Depends, HTTPException, status, APIRouter
from datetime import timedelta
from ..schemas.user import CreateUser, User, GetAllUsers, LoginUser
from ..schemas.token import Token
from ..schemas.message import Message
from ..models.user import DBUser
from ..utils import jwt as j


users_router = APIRouter(
    prefix="/user",
    tags=['users api'],
    responses={404: {"description": "Страница не найдена"}},
)

@users_router.post("/", response_model=User, responses={404: {"model":Message},
                                                          409: {"model":Message}
                                                          })
async def create_user(*, user: CreateUser) -> CreateUser:
    # добавить проверку роли
    passwd = j.get_password_hash(user.password)
    check_login = await DBUser.objects.get_or_none(login=user.login)

    if check_login != None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                detail=f"Пользователь с логином {check_login.login} уже существует")
    
    q = await DBUser.objects.create(login=user.login, fio=user.fio, password=passwd, role_id=user.role_id)
    
    user_data = User(
        user_id=q.user_id,
        login=user.login,
        fio=user.fio,
        role_id=user.role_id,
    )
    
    return user_data

@users_router.post("/auth", response_model=Token)
async def login_for_token(user: LoginUser) -> dict[str, str]:
    user = await j.authenticate_user(user.login, user.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=j.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = j.create_access_token(
        data={"sub": user.login}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@users_router.get("/", response_model=GetAllUsers, responses={
                                                404: {"model":Message},
                                                },
                   dependencies=[Depends(j.get_current_user)]
                                            )
async def get_users() -> GetAllUsers:

    users_data = await DBUser.objects.values(['user_id', 'login', 'fio','role_id'])

    data = GetAllUsers(
        users = users_data
    )

    return data