from config.database import database
from model.favorite_item import FavoriteItem


async def create_favorite(favorite: FavoriteItem):
    query = "INSERT INTO favorite_items (user_id, item_id) VALUES (:user_id, :item_id)"
    values = {"user_id": favorite.user_id, "item_id": favorite.item_id}
    await database.execute(query=query, values=values)


async def get_user_favorites(user_id: int):
    query = """
        SELECT items.*
        FROM favorite_items
        JOIN items ON favorite_items.item_id = items.id
        WHERE favorite_items.user_id = :user_id
    """
    return await database.fetch_all(query=query, values={"user_id": user_id})


async def get_favorite(user_id: int, item_id: int):
    query = "SELECT * FROM favorite_items WHERE user_id = :user_id AND item_id = :item_id"
    return await database.fetch_one(query=query, values={"user_id": user_id, "item_id": item_id})


async def delete_favorite(user_id: int, item_id: int):
    query = "DELETE FROM favorite_items WHERE user_id = :user_id AND item_id = :item_id"
    return await database.execute(query=query, values={"user_id": user_id, "item_id": item_id})