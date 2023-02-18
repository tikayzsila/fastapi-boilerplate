from fastapi import Depends, HTTPException, status, APIRouter, Request
import itertools
from ..schemas.role import GetAllRoles, Role, UpdateRole
from ..schemas.message import Message
from ..models.role import DBRole
from ..utils import jwt as j

roles_router = APIRouter(
    prefix="/role",
    tags=['roles api'],
    responses={404: {"description": "Страница не найдена"}},
)

async def check_admin_role(request: Request) -> None:
    
    roles_list = await DBRole.objects.values_list('name')
    roles = list(itertools.chain.from_iterable(roles_list))
    
    token = request.headers.get('authorization').split()
    user_role=await j.get_token_data(token[1])
    role = await DBRole.objects.filter(role_id=int(user_role[1])).values_list('name')
    
    role_exeption = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="not allowed",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if role[0][0] in roles:

        match role[0][0]:
            case 'admin':
                print('here')
                return status.HTTP_200_OK
            case 'user':
                print('here')
                raise role_exeption
    else:
 
        raise role_exeption
    

@roles_router.get("/",response_model=GetAllRoles, responses={
                                                404: {"model":Message},
                                                },
                   dependencies=[Depends(j.get_current_user), Depends(check_admin_role)]
                )
async def get_all_roles() -> GetAllRoles:
    roles_data = await DBRole.objects.values(['role_id', 'name', 'description'])
    print()
    return GetAllRoles(
        roles = roles_data
    )

@roles_router.put("/{id}", response_model=Role, responses={
                                                404: {"model":Message},
                                                },
                   dependencies=[Depends(j.get_current_user), Depends(check_admin_role)]
                                            )
async def update_role(id: int, data: UpdateRole) -> Role:
    
    role = await DBRole.objects.filter(role_id=id).get()
    await role.update(**{k: v for k, v in data.dict().items() if v})
    
    return Role(
        role_id=id,
        name=data.name,
        description=data.description,
    )

@roles_router.get("/{id}", response_model=Role, responses={
                                                404: {"model":Message},
                                                },
                   dependencies=[Depends(j.get_current_user), Depends(check_admin_role)]
                                            )
async def get_role(id: int) -> Role:

    data = await DBRole.objects.filter(role_id=id).values(['role_id', 'name', 'description'])

    return Role(
        role_id=data[0]['role_id'],
        name=data[0]['name'],
        description=data[0]['description'],
    )

