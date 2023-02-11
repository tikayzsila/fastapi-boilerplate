from fastapi import Depends, HTTPException, status, APIRouter
from ..schemas.role import CreateRole, GetAllRoles, Role
from ..schemas.message import Message
from ..models.role import DBRole
from ..utils import jwt as j

roles_router = APIRouter(
    prefix="/role",
    tags=['roles api'],
    responses={404: {"description": "Страница не найдена"}},
)

@roles_router.post("/",response_model=Role, responses={
                                                404: {"model":Message},
                                                },
                   dependencies=[Depends(j.get_current_user)]
                )
async def add_role(role: CreateRole) -> Role:
    
    q = await DBRole.objects.create(name=role.name, description=role.description)
    
    data = Role(
        id=q.role_id,
        name=q.name,
        description=q.description,
    )
    
    return data