from fastapi import APIRouter, Depends
from models.user import UserRecord
from services import auth_service

profile_router = APIRouter()

@profile_router.get("/profile")
def profile(user: UserRecord = Depends(auth_service.get_current_user)):
    return {"username": user.username, "roles": []}

@profile_router.get("/secret")
def secret(user: UserRecord = Depends(auth_service.get_current_user)):
    return {"secret": f"this is secret for {user.username}"}
