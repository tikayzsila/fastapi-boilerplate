from pydantic import BaseModel, Extra
from typing import List


class BaseUser(BaseModel):
    login: str


class CreateUser(BaseUser):
    password: str

    class Config:
        extra = Extra.allow


class User(BaseModel):
    user_id: int
    login: str


class LoginUser(BaseModel):
    login: str
    password: str


class GetAllUsers(BaseModel):
    users: List[User]


class UpdateUser(BaseModel):
    login: str
