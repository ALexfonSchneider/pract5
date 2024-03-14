import logging
import string
import logging
import jwt
from fastapi import APIRouter, Depends, Form, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter
from src.database import get_async_session

logger = logging.getLogger("debug")

router = APIRouter(prefix="/auth")

@router.post("/token", response_model=Token, responses={"401": {"detail": "message"}})
async def token(
    response: Response,
    username: str = Form(),
    password: str = Form(),
    session = Depends(get_async_session)
):
    user = await authenticate_user(session, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = craete_token(email=username)
    
    create_session(user.email, token)
    
    response.set_cookie("Authentication", token.access_token, max_age=60*ACCESS_TOKEN_EXPIRE_MINUTES)

    return token


@router.post("/login", response_model=LoginResult, responses={"401": {"detail": "message"}})
async def login(login_form: LoginForm, response: Response, session: AsyncSession = Depends(get_async_session)):
    user = await authenticate_user(session, login_form.email, login_form.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    token = craete_token(email=login_form.email)

    create_session(user.email, token)
    
    response.set_cookie("Authentication", token.access_token, max_age=60*ACCESS_TOKEN_EXPIRE_MINUTES)
    
    return LoginResult(
        **token.dict(),
        user=await crud.search_user_detail(session, user.user_id)
    )
    

@router.post("/refresh", response_model=Token, responses={"401": {"detail": "message"}})
async def refresh(refresh_form: RefreshTokenForm, session: AsyncSession = Depends(get_async_session)):
    try:
        payload = {
            **jwt.decode(refresh_form.refresh_token, SECRET_KEY2, algorithms=[ALGORITHM])
        }
    except:
        raise HTTPException(status_code=400, detail="Invalid token format")
    
    email = payload["email"]
    
    if not email:
        raise HTTPException(status_code=400)
    
    user: User = await crud.get_user_by_email(session, email=payload["email"])
    
    if not user:
        raise HTTPException(status_code=400)
    
    user_session = get_session(user.email)
    
    if user_session.refresh_token != refresh_form.refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = craete_token(user.email)
    
    create_session(user.email, token)
    
    return token