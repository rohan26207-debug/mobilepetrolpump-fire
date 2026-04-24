"""
Minimal FastAPI stub.

This project is a 100% offline React + localStorage petrol-pump app wrapped in an
Android WebView. The frontend makes zero calls to this backend. It exists only to
satisfy the supervisor program definition (`uvicorn server:app`) in the dev
environment. Keep this file tiny; do not add business logic here.
"""
from typing import Dict

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

app: FastAPI = FastAPI(title="M.Pump (offline) - idle backend")

api_router: APIRouter = APIRouter(prefix="/api")


@api_router.get("/")
async def root() -> Dict[str, str]:
    return {"status": "ok", "note": "Offline app - backend is idle."}


@api_router.get("/status")
async def status() -> Dict[str, str]:
    return {"status": "ok"}


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
