from fastapi import APIRouter, status, Depends
from model.chat_request import ChatRequest
from model.user_response import UserResponse
from service import chat_service
from service.auth_service import validate_user

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post("/", status_code=status.HTTP_200_OK)
async def ask_assistant(chat_request: ChatRequest, current_user: UserResponse = Depends(validate_user)):
    return await chat_service.ask_assistant(
        current_user.id,
        current_user.username,
        chat_request.prompt
    )


@router.delete("/", status_code=status.HTTP_200_OK)
async def reset_chat(current_user: UserResponse = Depends(validate_user)):
    return await chat_service.reset_chat(current_user.id)