import os
from ..models.user import DBUser
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from jose import JWTError, jwt

SECRET_KEY = os.environ.get('SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 500

auth_scheme = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_pass : str, hashed_pass : str) -> bool:
    return pwd_context.verify(plain_pass, hashed_pass)

def get_password_hash(password : str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict[str, str | None], expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_user_from_db(login : str) -> DBUser | None:
    return await DBUser.objects.get_or_none(login=login)

async def get_current_user(request: Request, token: str = Depends(auth_scheme)) -> DBUser:
    cred_exeption = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    auth = request.headers.get('authorization')
    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=401, 
            detail='Authorization header must start with Bearer')
    elif len(parts) == 1:
        raise HTTPException(
            status_code=401, 
            detail='Authorization token not found')
    elif len(parts) > 2:
        raise HTTPException(
            status_code=401, 
            detail='Authorization header be Bearer token')
    
    token = parts[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        login: str = payload.get("sub")
        if login is None:
            raise cred_exeption
    except JWTError:
        raise cred_exeption

    user = await get_user_from_db(login=login)
    
    if user is None:
        raise cred_exeption
    return user

async def authenticate_user(login: str, password: str) -> DBUser | bool:
    user = await get_user_from_db(login=login)

    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user