import json
from .db import URL
from asyncpg.exceptions import UniqueViolationError
from ..models.user import DBUser
from ..models.role import DBRole

async def get_data_from_file(table_name):
    f = open("seed.json")
    data = json.load(f)
    return data[f'{table_name}']
        
async def seed_data(table_name):
    raw_data =  await get_data_from_file(table_name)
    match table_name:
        case "roles":
            try:
                for v in raw_data:
                    await DBRole.objects.create(name=v['name'], description=v['description'])
                    print("seed roles")
            except UniqueViolationError:
                print("roles data already in db")
                
        case "users":
            try:
                for v in raw_data:
                    await DBUser.objects.create(
                        login=v['login'],
                        fio=v['fio'],
                        role_id=v['role_id'],
                        password=v['password']
                    )
                    print("seed users")
            except UniqueViolationError:
                print("seed users data already in db")
