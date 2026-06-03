from fastapi import status
from starlette.exceptions import HTTPException


def token_exception():
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED ,
        detail="The token provided is invalid"
    )
    return credential_exception

def username_taken_exception():
    username_taken_exception_response = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Provided username already taken"
    )
    return username_taken_exception_response

def username_credentials_exception():
    token_exception_response = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED ,
        detail="Incorrect username or password"
    )
    return token_exception_response

def favorite_already_exists_exception():
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Item already exists in favorites"
    )

def item_out_of_stock_exception():
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Not enough items in stock"
    )

def chat_limit_exception():
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Chat prompt limit reached"
    )

def email_taken_exception():
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Email already exists"
    )