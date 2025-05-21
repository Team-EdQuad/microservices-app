import httpx
from fastapi import HTTPException, Request, APIRouter, Depends
from typing import Optional

USER_MANAGEMENT_SERVICE_URL = "http://127.0.0.1:8001"

router = APIRouter()