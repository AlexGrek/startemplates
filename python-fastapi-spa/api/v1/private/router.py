from fastapi import APIRouter, Depends

from services import auth_service
from api.v1.private.profile import profile_router

protected_router = APIRouter(prefix="/private", tags=["private"], dependencies=[Depends(auth_service.get_current_user)])

protected_router.include_router(profile_router)
