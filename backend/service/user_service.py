from typing import List, Optional
from passlib.context import CryptContext
from exceptions.exception import username_taken_exception, email_taken_exception
from model.user import User
from model.user_request import UserRequest
from model.user_response import UserResponse
from repository import user_repository

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return bcrypt_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt_context.verify(plain_password, hashed_password)


async def validate_unique_username(username: str) -> bool:
    existing_user = await user_repository.get_user_by_username(username)
    return existing_user is None


def build_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        phone=user.phone,
        country=user.country,
        city=user.city,
        username=user.username
    )


def build_user_from_record(user_record) -> User:
    return User(
        id=user_record["id"],
        first_name=user_record["first_name"],
        last_name=user_record["last_name"],
        email=user_record["email"],
        phone=user_record["phone"],
        country=user_record["country"],
        city=user_record["city"],
        username=user_record["username"],
        hashed_password=user_record["hashed_password"]
    )


async def create_user(user_request: UserRequest) -> UserResponse:
    if not await validate_unique_username(user_request.username):
        raise username_taken_exception()

    if not await validate_unique_email(user_request.email):
        raise email_taken_exception()

    hashed_password = get_password_hash(user_request.password)
    created_user_record = await user_repository.create_user(user_request, hashed_password)
    created_user = build_user_from_record(created_user_record)
    return build_user_response(created_user)


async def get_user_by_id(user_id: int) -> Optional[UserResponse]:
    user_record = await user_repository.get_user_by_id(user_id)
    if not user_record:
        return None
    user = build_user_from_record(user_record)
    return build_user_response(user)


async def get_users() -> List[UserResponse]:
    user_records = await user_repository.get_users()
    users = [build_user_from_record(user_record) for user_record in user_records]
    return [build_user_response(user) for user in users]


async def get_user_by_username(username: str) -> Optional[User]:
    user_record = await user_repository.get_user_by_username(username)
    if not user_record:
        return None
    return build_user_from_record(user_record)


async def delete_user(user_id: int):
    existing_user = await user_repository.get_user_by_id(user_id)
    if not existing_user:
        return None
    await user_repository.delete_user(user_id)
    return build_user_response(build_user_from_record(existing_user))


async def validate_unique_email(email: str) -> bool:
    existing_email = await user_repository.get_user_by_email(email)
    return existing_email is None