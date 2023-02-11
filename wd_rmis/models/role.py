import ormar
from ..utils.db import BaseMeta

class DBRole(ormar.Model):
    class Meta(BaseMeta):
        tablename = "roles"

    role_id : int = ormar.Integer(primary_key=True)
    name: str = ormar.String(max_length=64, unique=True)
    description : str = ormar.String(max_length=128)