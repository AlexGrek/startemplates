from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.auth.auth import auth_router
from api.v1.private.router import protected_router
from api.v1.websocket import ws_router
from storage.usersyaml import _ensure_users_file_exists

app = FastAPI(title="AuthenticatedService", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(protected_router, prefix="/api/v1")
app.include_router(ws_router, prefix="/api/v1")

_ensure_users_file_exists()


@app.get("/")
def root():
    return {"msg": "Auth demo running. See /docs for API docs."}
