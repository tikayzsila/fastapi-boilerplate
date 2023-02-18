from pydantic import BaseModel, Extra
from typing import List

class BaseUser(BaseModel):
    login: str
    role_id: int 

class CreateUser(BaseUser):
    password: str

    class Config:
        extra = Extra.allow

class User(BaseModel):
    user_id: int
    login: str
    role_id: int

class LoginUser(BaseModel):
    login: str
    password: str

class GetAllUsers(BaseModel):
    users: List[User]

class UpdateUser(BaseModel):
    login: str
    role_id: int
