from pydantic import BaseModel

class JWTTokenModel(BaseModel):
    access_token: str
    token_type: str = 'bearer'