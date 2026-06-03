from fastapi import APIRouter, status, Depends
from model.item import Item
from model.user_response import UserResponse
from service import item_service
from service.auth_service import validate_user

router = APIRouter(
    prefix="/item",
    tags=["item"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_item(item: Item, current_user: UserResponse = Depends(validate_user)):
    return await item_service.create_item(item)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_items():
    return await item_service.get_items()


@router.get("/search/", status_code=status.HTTP_200_OK)
async def search_items_by_name(name: str):
    return await item_service.search_items_by_name(name)


@router.get("/search/price", status_code=status.HTTP_200_OK)
async def search_items_by_price(operator: str, price: float):
    return await item_service.search_items_by_price(operator, price)


@router.get("/search/filter", status_code=status.HTTP_200_OK)
async def search_items(
    name: str = "",
    min_price: float = 0,
    max_price: float = 999999,
    min_stock: int = 0,
    max_stock: int = 999999,
    in_stock_only: bool = False,
    sort_by: str = "name"
):
    return await item_service.search_items(name, min_price, max_price, min_stock, max_stock, in_stock_only, sort_by)


@router.get("/{item_id}", status_code=status.HTTP_200_OK)
async def get_item_by_id(item_id: int):
    return await item_service.get_item_by_id(item_id)


@router.delete("/{item_id}", status_code=status.HTTP_200_OK)
async def delete_item(item_id: int, current_user: UserResponse = Depends(validate_user)):
    return await item_service.delete_item(item_id)


@router.put("/{item_id}/stock", status_code=status.HTTP_200_OK)
async def update_item_stock(item_id: int, stock: int, current_user: UserResponse = Depends(validate_user)):
    return await item_service.update_item_stock(item_id, stock)