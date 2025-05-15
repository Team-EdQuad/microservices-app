from fastapi import FastAPI
from .services.test import router as item_router

app = FastAPI(title="Dashboard Management API")

app.include_router(item_router, prefix="/item", tags=["nonacademic"])