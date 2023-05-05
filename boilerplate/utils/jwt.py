from ..models.user import DBUser
from ..models.users_tokens import DBUsersTokens
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from authlib.jose import jwt, errors
import secrets

ALGORITHM = {"alg": "HS256"}
USERS_TO_CHECK: dict = {}
auth_scheme = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_user_key():
    return secrets.token_urlsafe(32)


async def get_users_key(id: int | None):
    data = await DBUser.objects.filter(user_id=id).values_list(flatten=True, fields="key")
    return data[0]


def verify_password(plain_pass: str, hashed_pass: str) -> bool:
    return pwd_context.verify(plain_pass, hashed_pass)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(
    user_key: str | None,
    data: dict[str, str | None],
    expires_delta: timedelta | None = None,
) -> bytes:
    to_encode: dict[str, str | None] = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": str(expire)})
    encoded_jwt = jwt.encode(header=ALGORITHM, payload=to_encode, key=user_key)
    return encoded_jwt


async def get_user_from_db(login: str) -> DBUser | None:
    return await DBUser.objects.get_or_none(login=login)


async def get_current_user(request: Request, token: str = Depends(auth_scheme)) -> None:
    cred_exeption = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    auth = request.headers.get("authorization")

    if auth:
        parts = auth.split()

    if parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Authorization header must start with Bearer")
    elif len(parts) == 1:
        raise HTTPException(status_code=401, detail="Authorization token not found")
    elif len(parts) > 2:
        raise HTTPException(status_code=401, detail="Authorization header be Bearer token")

    token = parts[1]
    user_id = await DBUsersTokens.objects.filter(acc_token=token).values_list(flatten=True, fields="user_id")
    try:
        user_key = await get_users_key(user_id[0])
        payload = jwt.decode(token, user_key)
        login: str = payload.get("sub")
        if login is None:
            raise cred_exeption
    except (errors.BadSignatureError, IndexError):
        raise cred_exeption

    if await get_user_from_db(login=login) is None:
        raise cred_exeption


async def authenticate_user(login: str, password: str) -> DBUser | bool:
    user = await get_user_from_db(login=login)

    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


async def get_token_data(token: str):
    cred_exeption = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        user_id = await DBUsersTokens.objects.filter(acc_token=token).values_list(flatten=True, fields="user_id")
        user_key = await get_users_key(user_id[0])
        # добавить метод для получения пейлоада токена
        payload = jwt.decode(token, user_key)
        data: str = payload.get("sub")

        if data is None:
            raise cred_exeption
    except errors.BadSignatureError:
        raise cred_exeption

    return data.split(",")
