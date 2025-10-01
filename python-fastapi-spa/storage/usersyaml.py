import os
from typing import Any, Dict, List, Optional
import yaml
from config.config import USERS_FILE, _users_file_lock
from models.user import UserRecord


def _ensure_users_file_exists():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            yaml.safe_dump({"users": []}, f)

def load_users_dict() -> Dict[str, Any]:
    """Read users.yaml every time (as requested)."""
    _ensure_users_file_exists()
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    # Normalize
    users = data.get("users", [])
    return {"users": users}

def save_users_dict(data: Dict[str, Any]) -> None:
    """Write users.yaml with a simple file lock to avoid concurrent writes."""
    with _users_file_lock:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f)

def find_user(username: str) -> Optional[UserRecord]:
    data = load_users_dict()
    for u in data.get("users", []):
        if u.get("username") == username:
            return UserRecord(**u)
    return None

def add_user(username: str, password_hash: str, roles: Optional[List[str]] = None) -> UserRecord:
    data = load_users_dict()
    users = data.get("users", [])
    # Ensure unique
    if any(u.get("username") == username for u in users):
        raise ValueError("User already exists")
    new = {"username": username, "password_hash": password_hash}
    users.append(new)
    data["users"] = users
    save_users_dict(data)
    return UserRecord(**new)
