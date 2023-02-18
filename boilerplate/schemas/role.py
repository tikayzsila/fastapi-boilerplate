from pydantic import BaseModel
from typing import List, Optional

class Role(BaseModel):
    role_id: int
    name: str
    description: str

class CreateRole(BaseModel):
    name: str
    description: str

class UpdateRole(BaseModel):
    name: str
    description: Optional[str]

class GetAllRoles(BaseModel):
    roles: List[Role]
