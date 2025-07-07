from fastapi import APIRouter, HTTPException, Header
from app.models.user_model import DeleteUserRequest
from app.utils.validation import verify_admin_token
from app.services.delete_user_service import delete_user_account
from fastapi import Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()
router = APIRouter()

# @router.delete("/delete_user")
# async def delete_user(request: DeleteUserRequest, authorization: str = Header(...)):
#     # Check if the token is a valid admin token
#     is_admin = await verify_admin_token(authorization)
#     if not is_admin:
#         raise HTTPException(status_code=403, detail="Admin privileges required")

#     # Admin is verified, proceed to delete the user
#     message = await delete_user_account(request.username, request.password)
#     return {"message": message}

@router.delete("/delete_user")
async def delete_user(
    request: DeleteUserRequest,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    authorization = credentials.credentials  # Extract the token string
    is_admin = await verify_admin_token(authorization)
    if not is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")

    message = await delete_user_account(request.username, request.password)
    return {"message": message}