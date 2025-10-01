from typing import Any, Optional
from fastapi import (
    Depends,
    HTTPException,
    Request,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.security import HTTPBearer
from config.jwt_config import *
from storage.usersyaml import find_user

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request, auth: Optional[Any] = Depends(bearer_scheme)
):
    """
    Try Bearer token first (Authorization header), fallback to cookie 'access_token'.
    Raises 401 if missing/invalid.
    Returns user record (dict).
    """
    token: Optional[str] = None
    if auth and getattr(auth, "credentials", None):
        token = auth.credentials
    if not token:
        token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    payload = decode_token(token)
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
        )
    user = find_user(username)
    if not user:
        # Token valid but user not found (deleted) -> unauthorized
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    return user


async def get_websocket_user(websocket: WebSocket, token: str):
    """
    Authenticates a user via a token in the WebSocket URL query parameter.
    """
    payload = decode_token(token)
    username = payload.get("sub")
    if not username:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token payload"
        )
        raise WebSocketDisconnect

    user = find_user(username)
    if not user:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION, reason="User not found"
        )
        raise WebSocketDisconnect

    return user


async def get_websocket_user_header(websocket: WebSocket):
    """
    Authenticates a user via a token in the 'Authorization' header.
    """
    token = websocket.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Missing or invalid token in header",
        )
        raise WebSocketDisconnect

    token = token.split(" ")[1]  # Extract the token part
    payload = decode_token(token)
    username = payload.get("sub")
    if not username:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token payload"
        )
        raise WebSocketDisconnect

    user = find_user(username)
    if not user:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION, reason="User not found"
        )
        raise WebSocketDisconnect

    return user
