from fastapi import FastAPI, APIRouter
# Initialize FastAPI app and router
app = FastAPI(title="Academic API")
router = APIRouter()

# # Include routers for student and teacher endpoints
# app.include_router(academic_student.router, tags=["Endpoints student"])
# app.include_router(academic_teacher.router, tags=["Endpoints teacher"])

# Define a root endpoint
@app.get("/")
async def homepage():
    return {"message": "Welcome to the Behaviral analysis API"}

# Include the router
app.include_router(router)









