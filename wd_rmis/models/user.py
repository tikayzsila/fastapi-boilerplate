import ormar
from ..utils.db import BaseMeta
from .role import DBRole

class DBUser(ormar.Model):
    class Meta(BaseMeta):
        tablename = "users"
    
    user_id : int = ormar.Integer(primary_key=True)
    login: str = ormar.String(max_length=64, unique=True)
    fio : str = ormar.String(max_length=128)
    password : str = ormar.String(max_length=128)
    role_id : int = ormar.ForeignKey(DBRole)