from model.favorite_item import FavoriteItem
from repository import favorite_repository
from service import item_service
from exceptions.exception import favorite_already_exists_exception


async def create_favorite(user_id: int, item_id: int):
    existing_favorite = await favorite_repository.get_favorite(user_id, item_id)
    if existing_favorite:
        raise favorite_already_exists_exception()
    favorite = FavoriteItem(user_id=user_id, item_id=item_id)
    await favorite_repository.create_favorite(favorite)
    return {"message": "Item added to favorites successfully"}


async def get_user_favorites(user_id: int):
    items = await favorite_repository.get_user_favorites(user_id)
    return [item_service.build_item(item) for item in items]


async def delete_favorite(user_id: int, item_id: int):
    await favorite_repository.delete_favorite(user_id, item_id)
    return {"message": "Item removed from favorites successfully"}