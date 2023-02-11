from pydantic import BaseModel
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    role_id: int
    user_id: int