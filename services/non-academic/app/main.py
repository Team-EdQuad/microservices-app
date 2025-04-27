from fastapi import FastAPI
from .services.nonacademic import sports_router, clubs_router
from .services.nonacademic import router as nonacademic_router

app = FastAPI(title="Non-Academic Management API")


app.include_router(sports_router, prefix="/sports", tags=["sports"])
app.include_router(clubs_router, prefix="/clubs", tags= ["clubs"])
app.include_router(nonacademic_router, prefix="/item", tags=["nonacademic"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)