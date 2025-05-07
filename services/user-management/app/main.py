from fastapi import FastAPI
from app.routers import login

app = FastAPI()

app.include_router(login.router, prefix="/auth")

@app.get("/")
async def read_root():
    return {"message": "User Management Service Running"}
