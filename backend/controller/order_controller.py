from fastapi import APIRouter, status, Depends
from model.user_response import UserResponse
from service import order_service
from service.auth_service import validate_user

router = APIRouter(
    prefix="/order",
    tags=["Order"]
)


@router.post("/item/{item_id}", status_code=status.HTTP_201_CREATED)
async def add_item_to_order(item_id: int, quantity: int, current_user: UserResponse = Depends(validate_user)):
    shipping_address = f"{current_user.country}, {current_user.city}"
    return await order_service.add_item_to_order(current_user.id, item_id, quantity, shipping_address)


@router.get("/items", status_code=status.HTTP_200_OK)
async def get_order_items(current_user: UserResponse = Depends(validate_user)):
    return await order_service.get_order_items(current_user.id)


@router.delete("/item/{item_id}", status_code=status.HTTP_200_OK)
async def remove_item_from_order(item_id: int, current_user: UserResponse = Depends(validate_user)):
    return await order_service.remove_item_from_order(current_user.id, item_id)


@router.put("/purchase", status_code=status.HTTP_200_OK)
async def purchase_order(current_user: UserResponse = Depends(validate_user)):
    return await order_service.purchase_order(current_user.id)


@router.delete("/temp", status_code=status.HTTP_200_OK)
async def delete_temp_order(current_user: UserResponse = Depends(validate_user)):
    return await order_service.delete_temp_order(current_user.id)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user_orders(current_user: UserResponse = Depends(validate_user)):
    return await order_service.get_user_orders(current_user.id)


@router.put("/item/{item_id}/quantity", status_code=status.HTTP_200_OK)
async def update_order_item_quantity(item_id: int, quantity: int, current_user: UserResponse = Depends(validate_user)):
    return await order_service.update_order_item_quantity(current_user.id, item_id, quantity)


@router.get("/{order_id}", status_code=status.HTTP_200_OK)
async def get_order_by_id(order_id: int, current_user: UserResponse = Depends(validate_user)):
    return await order_service.get_order_by_id(current_user.id, order_id)