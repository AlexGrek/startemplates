from typing import List, Optional
from pydantic import BaseModel


class UserRecord(BaseModel):
    username: str
    password_hash: str
