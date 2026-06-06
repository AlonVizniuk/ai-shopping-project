from fastapi import APIRouter, Depends, status
from model.user_response import UserResponse
from service import prediction_service
from service.auth_service import validate_user


router = APIRouter(prefix="/prediction", tags=["Prediction"])


@router.get("/future-spending", status_code=status.HTTP_200_OK)
async def predict_future_spending(current_user: UserResponse = Depends(validate_user)):
    return await prediction_service.predict_future_spending(current_user.id)