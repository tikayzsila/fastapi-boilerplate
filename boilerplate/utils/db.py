import databases
import ormar
import os
import sqlalchemy
import subprocess

db_port = os.environ.get("PG_PORT")
db_name = os.environ.get("PG_DB")
db_host = os.environ.get("PG_HOST")
db_user = os.environ.get("PG_USER")
db_password = os.environ.get("PG_PASSWORD")

URL: str = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?sslmode=disable"

database = databases.Database(URL)
metadata = sqlalchemy.MetaData()


class BaseMeta(ormar.ModelMeta):
    database = database
    metadata = metadata


async def wait_and_migrate():
    subprocess.run("alembic upgrade head", shell=True, check=True)
    print("Postgres is up - executing command")
