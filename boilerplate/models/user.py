import ormar
from ..utils.db import BaseMeta

class DBUser(ormar.Model):
    class Meta(BaseMeta):
        tablename = "users"
    
    user_id : int = ormar.Integer(primary_key=True)
    login: str = ormar.String(max_length=64, unique=True)
    key: str = ormar.String(max_length=200, unique=True)
    password : str = ormar.String(max_length=128)