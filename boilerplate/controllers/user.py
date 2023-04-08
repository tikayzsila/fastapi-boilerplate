from fastapi import Depends, HTTPException, status, APIRouter
from datetime import timedelta, datetime
import os
from ..schemas.user import CreateUser, User, GetAllUsers, LoginUser, UpdateUser
from ..schemas.token import Token
from ..models.user import DBUser
from ..models.users_tokens import DBUsersTokens
from ..utils import jwt as j

users_router = APIRouter(
    prefix="/user",
    tags=['users api'],
    responses={404: {"description": "Страница не найдена"}},
)

@users_router.post("/", response_model=User)
async def create_user(*, user: CreateUser) -> CreateUser:
    passwd = j.get_password_hash(user.password)
    key = j.create_user_key()
    check_login = await DBUser.objects.get_or_none(login=user.login)
    if check_login != None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                detail=f"Пользователь с логином {check_login.login} уже существует")
    
    q = await DBUser.objects.create(login=user.login, password=passwd, key=key)
    user_data = User(
        user_id=q.user_id,
        login=user.login,
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
    user_data = await DBUser.objects.filter(login=user.login).values(['user_id', 'login', 'key'])
    payload_string = user_data[0]['login']
    
    access_token_expires = timedelta(minutes=int(os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES')))
    access_token = j.create_access_token(
        user_key=user_data[0]['key'],
        data={"sub": payload_string}, 
        expires_delta=access_token_expires
    )
    d = await DBUsersTokens.objects.filter(user_id=user_data[0]['user_id'], exp_time__lt=datetime.now()).delete(each=True)
    print(d)
    await DBUsersTokens.objects.create(
        user_id=user_data[0]['user_id'], 
        acc_token=access_token.decode('utf-8')
    )
    return {"access_token": access_token, "token_type": "bearer"}

@users_router.get("/", response_model=GetAllUsers,
                   dependencies=[Depends(j.get_current_user)]
                                            )
async def get_users() -> GetAllUsers:

    users_data = await DBUser.objects.values(['user_id', 'login'])

    return GetAllUsers(
        users = users_data
    )

@users_router.put("/{id}", response_model=User,
                   dependencies=[Depends(j.get_current_user)]
                                            )
async def update_user(id: int, data: UpdateUser) -> User:
    
    user = await DBUser.objects.filter(user_id=id).get()
    await user.update(**{k: v for k, v in data.dict().items() if v})
    
    return User(
        user_id=id,
        login=data.login,
    )

@users_router.get("/{id}", response_model=User,
                   dependencies=[Depends(j.get_current_user)]
                                            )
async def get_user(id: int) -> User:

    users_data = await DBUser.objects.filter(user_id=id).values(['user_id', 'login'])
    return User(
        user_id=users_data[0]['user_id'],
        login=users_data[0]['login'],
    )

