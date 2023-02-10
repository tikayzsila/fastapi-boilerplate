from ..schemas.token import TokenData
import os
from ..models.user import DBUser
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

SECRET_KEY = os.environ.get('SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 500

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")
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

async def get_current_user(token: str = Depends(oauth2_scheme)) -> DBUser:
    cred_exeption = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        login: str = payload.get("sub")
        
        print(login)
        
        if login is None:
            raise cred_exeption
        token_data = TokenData(login=login)
    except JWTError:
        raise cred_exeption
    user = await get_user_from_db(login=token_data.login, role=token_data.role)
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