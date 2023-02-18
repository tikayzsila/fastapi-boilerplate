from pydantic import BaseModel, Extra
from ..models.user import DBUser
from typing import List

class CreateUser(BaseModel):
    login: str
    fio: str
    role_id: int
    password: str
#    confirm_password: str

    class Config:
        extra = Extra.allow

class User(BaseModel):
    user_id: int
    login: str
    fio: str
    role_id: int

class LoginUser(BaseModel):
    login: str
    password: str

class GetAllUsers(BaseModel):
    users: List[User]

