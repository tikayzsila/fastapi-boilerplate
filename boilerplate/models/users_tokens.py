import ormar, os
from ..utils.db import BaseMeta
from datetime import datetime, timedelta
from .user import DBUser

class DBUsersTokens(ormar.Model):
    class Meta(BaseMeta):
        tablename = "users_tokens"
    
    id : int = ormar.Integer(primary_key=True, autoincrement=True)
    user_id: int = ormar.ForeignKey(DBUser)
    acc_token: str = ormar.String(max_length=200, unique=True)
    exp_time : datetime = ormar.DateTime(
        timezone=True, 
        default=datetime.now()+timedelta(
            minutes=int(os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES'))
        )
    )