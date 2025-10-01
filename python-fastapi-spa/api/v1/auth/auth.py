# /api/v1/auth/register
import os

from fastapi import APIRouter, HTTPException, Response, status, Request

from config.auth import hash_password, verify_password
from config.config import ACCESS_TOKEN_EXPIRE_MINUTES
from config.jwt_config import create_access_token, decode_token
from schemas.auth import LoginIn, RegisterIn, TokenOut
from storage.usersyaml import add_user, find_user


auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post(
    "/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED
)
def register(payload: RegisterIn, response: Response):
    # Simple validations - username uniqueness
    if find_user(payload.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
        )
    password_hash = hash_password(payload.password)
    try:
        add_user(payload.username, password_hash)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
        )
    # Auto login
    token = create_access_token(subject=payload.username)
    # set cookie
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=bool(os.getenv("SECURE_COOKIES", "1") == "1"),
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return TokenOut(access_token=token)


# /api/v1/auth/login
@auth_router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, response: Response):
    user = find_user(payload.username)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    token = create_access_token(subject=payload.username)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=bool(os.getenv("SECURE_COOKIES", "1") == "1"),
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return TokenOut(access_token=token)


@auth_router.get("/whoami")
def whoami(request: Request):
    """
    Public diagnostic endpoint. If cookie present and valid, returns username; otherwise empty.
    Useful for SPA to detect session without explicit login call.
    """
    
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return {"username": payload.get("sub")}
