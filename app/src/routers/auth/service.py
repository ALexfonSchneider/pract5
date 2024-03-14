from fastapi import HTTPException, Request
import jwt
import requests
import datetime
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from config import ALGORITHM, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY2, REFRESH_TOKEN_EXPIRE_MINUTES
from datetime import datetime, timedelta
from fastapi import status


def get_authorization_scheme_param(
    authorization_header_value: str | None,
) -> tuple[str, str]:
    if not authorization_header_value:
        return "", ""
    scheme, _, param = authorization_header_value.partition(" ")
    return scheme, param


class OAuth2PasswordBearerWithCookie(OAuth2PasswordBearer):
    async def __call__(self, request: Request):
        authorization = request.headers.get("Authorization")
        if authorization:
            scheme, param = get_authorization_scheme_param(authorization)
            if not authorization or scheme.lower() != "bearer":
                if self.auto_error:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Not authenticated",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                else:
                    return None
            return param
        else:
            return request.cookies.get("Authentication")


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="auth/token")


def verify_password(email: str, password: str):
    response = requests.post("https://ternex.ru/api/1/password-validate", json={
        'password': password,
        'email': email
    }).json()
    return response['valid']


async def authenticate_user(session: AsyncSession, email: str, password: str):
    user: User = await get_user_by_email(session, email)
    if not user:
        return None
    if not verify_password(user.email, password):
        return None
    return user


def create_access_token(email: str, expires_minutes: int | None = ACCESS_TOKEN_EXPIRE_MINUTES):
    data = {
        "email": email, 
        "exp": datetime.now() + timedelta(minutes=expires_minutes)
    }
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return access_token


def create_refresh_token(email: str, expires_minutes: int | None = REFRESH_TOKEN_EXPIRE_MINUTES):
    data = {
        "email": email, 
        "exp": datetime.now() + timedelta(minutes=expires_minutes)
    }
    access_token = jwt.encode(data, SECRET_KEY2, algorithm=ALGORITHM)
    return access_token


def craete_token(email: str, access_token_expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES, refresh_token_expires_minutes: int = REFRESH_TOKEN_EXPIRE_MINUTES) -> Token:
    access_token = create_access_token(email)
    refresh_token = create_refresh_token(email)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        access_token_expires=datetime.now() + timedelta(minutes=access_token_expires_minutes),
        refresh_token_expires=datetime.now() + timedelta(minutes=refresh_token_expires_minutes),
        token_type="bearer"
    )