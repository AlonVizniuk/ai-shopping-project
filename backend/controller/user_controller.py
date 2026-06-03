from fastapi import APIRouter, status, Depends
from model.user_request import UserRequest
from model.user_response import UserResponse
from service import user_service
from service.auth_service import validate_user

router = APIRouter(
    prefix="/user",
    tags=["user"]
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(user_request: UserRequest) -> UserResponse:
    return await user_service.create_user(user_request)


@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_user_by_id(user_id: int, current_user: UserResponse = Depends(validate_user)) -> UserResponse:
    return await user_service.get_user_by_id(user_id)


@router.delete("/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def delete_current_user(current_user: UserResponse = Depends(validate_user)):
    return await user_service.delete_user(current_user.id)


@router.delete("/{user_id}", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def delete_user(user_id: int, current_user: UserResponse = Depends(validate_user)):
    return await user_service.delete_user(user_id)


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[UserResponse])
async def get_users(current_user: UserResponse = Depends(validate_user)):
    return await user_service.get_users()