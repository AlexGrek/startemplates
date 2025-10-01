import datetime
from typing import Any, Dict, Optional
import uuid

from fastapi import HTTPException, status
from config.config import *
from jose import jwt, JWTError


def create_access_token(*, subject: str, expires_delta: Optional[datetime.timedelta] = None) -> str:
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    expire = now + (expires_delta or datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "jti": str(uuid.uuid4()),
    }
    token = jwt.encode(to_encode, JWT_SECRET or "", algorithm=JWT_ALGORITHM)
    return token

def decode_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, JWT_SECRET or "", algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
