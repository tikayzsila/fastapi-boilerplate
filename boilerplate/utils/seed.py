import json
import os
import logging
from asyncpg.exceptions import UniqueViolationError
from ..models.user import DBUser
from .jwt import get_password_hash
from jinja2 import Environment, FileSystemLoader


log = logging.getLogger(__name__)


async def generate_seed_file():
    env = Environment(loader=FileSystemLoader(""), trim_blocks=True, lstrip_blocks=True)
    templ = env.get_template("seed.j2")

    admin_data = {}
    admin_data["adm_login"] = os.environ.get("DEFAULT_ADMIN_USERNAME")
    admin_data["adm_password"] = os.environ.get("DEFAULT_ADMIN_PASSWORD")
    data = templ.render(admin_data)
    return json.loads(data)


async def get_data_from_file(table_name):
    data = await generate_seed_file()
    return data[f"{table_name}"]


async def seed_data(table_name):
    raw_data = await get_data_from_file(table_name)
    match table_name:
        case "users":
            try:
                for v in raw_data:
                    await DBUser.objects.create(
                        login=v["login"],
                        password=get_password_hash(v["password"]),
                        key=v["key"],
                    )
                log.info("seed users")
            except UniqueViolationError:
                log.info("seed users data already in db")
