from fastapi import APIRouter, status, Depends
from model.user_response import UserResponse
from service import favorite_service
from service.auth_service import validate_user

router = APIRouter(
    prefix="/favorite",
    tags=["Favorite"]
)

@router.post("/{item_id}", status_code=status.HTTP_201_CREATED)
async def create_favorite(item_id: int, current_user: UserResponse = Depends(validate_user)):
    return await favorite_service.create_favorite(current_user.id, item_id)

@router.get("/", status_code=status.HTTP_200_OK)
async def get_user_favorites(current_user: UserResponse = Depends(validate_user)):
    return await favorite_service.get_user_favorites(current_user.id)

@router.delete("/{item_id}", status_code=status.HTTP_200_OK)
async def delete_favorite(item_id: int, current_user: UserResponse = Depends(validate_user)):
    return await favorite_service.delete_favorite(current_user.id, item_id)