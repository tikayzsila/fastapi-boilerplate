import databases
import ormar
import os
from typing import Union
import sqlalchemy

db_port : Union[None, str] = os.environ.get('PG_PORT')
db_name : Union[None, str] = os.environ.get('PG_DB')
db_host : Union[None, str] = os.environ.get('PG_HOST')
db_user : Union[None, str] = os.environ.get('PG_USER')
db_password : Union[None, str] = os.environ.get('PG_PASSWORD')

URL : str = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

database = databases.Database(URL)
metadata = sqlalchemy.MetaData()

class BaseMeta(ormar.ModelMeta):
    database = database
    metadata = metadata
