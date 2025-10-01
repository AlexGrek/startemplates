import os
from threading import Lock


USERS_FILE = os.getenv("USERS_FILE", "users.yaml")
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET must be set in environment (e.g. via .env).")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "525948")
)  # 1 year in minutes

_users_file_lock = Lock()
