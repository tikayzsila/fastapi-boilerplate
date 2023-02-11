from pydantic import BaseModel
from typing import List

class CreateRole(BaseModel):
    name: str
    description: str

class Role(BaseModel):
    id: int
    name: str
    description: str

class GetAllRoles(BaseModel):
    roles: List[Role]
