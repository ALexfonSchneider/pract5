from pydantic import BaseModel
from datetime import datetime

class TokenData(BaseModel):
    email: str
    exp: datetime
    

class AccessToken(BaseModel):
    access_token: str
    access_token_expires: datetime
    

class RefreshToken(BaseModel):
    refresh_token: str
    refresh_token_expires: datetime
    

class Token(AccessToken, RefreshToken):
    token_type: str