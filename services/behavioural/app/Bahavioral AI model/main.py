from fastapi import FastAPI
from predict_active_time import router as predict_router

app = FastAPI()
app.include_router(predict_router, prefix="/api")