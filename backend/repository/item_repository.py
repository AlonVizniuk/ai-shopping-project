from config.database import database
from model.item import Item


async def create_item(item: Item):
    query = """
        INSERT INTO items (name, price, stock)
        VALUES (:name, :price, :stock)
    """
    values = {
        "name": item.name,
        "price": item.price,
        "stock": item.stock
    }
    await database.execute(query=query, values=values)
    created_id = await database.fetch_val(query="SELECT LAST_INSERT_ID()")
    return await get_item_by_id(created_id)


async def get_item_by_id(item_id: int):
    query = "SELECT * FROM items WHERE id = :item_id"
    return await database.fetch_one(query=query, values={"item_id": item_id})


async def get_items():
    query = "SELECT * FROM items"
    return await database.fetch_all(query=query)

async def delete_item(item_id: int):
    query = "DELETE FROM items WHERE id = :item_id"
    return await database.execute(query=query, values={"item_id": item_id})

async def update_item_stock(item_id: int, stock: int):
    query = "UPDATE items SET stock = :stock WHERE id = :item_id"
    await database.execute(query=query, values={"item_id": item_id, "stock": stock})
    return await get_item_by_id(item_id)


async def search_items_by_name(name: str):
    query = "SELECT * FROM items WHERE name LIKE :name"
    return await database.fetch_all(query=query, values={"name": f"%{name}%"})


async def search_items_by_price(operator: str, price: float):
    query = f"SELECT * FROM items WHERE price {operator} :price"
    return await database.fetch_all(query=query, values={"price": price})


async def search_items(name: str = "", min_price: float = 0, max_price: float = 999999, min_stock: int = 0, max_stock: int = 999999, in_stock_only: bool = False, sort_by: str = "name"):
    words = [word.strip() for word in name.split(",") if word.strip()]

    query = """
        SELECT * FROM items
        WHERE price >= :min_price
        AND price <= :max_price
        AND stock >= :min_stock
        AND stock <= :max_stock
    """

    values = {
        "min_price": min_price,
        "max_price": max_price,
        "min_stock": min_stock,
        "max_stock": max_stock
    }

    if words:
        name_filters = []
        for index, word in enumerate(words):
            key = f"name_{index}"
            name_filters.append(f"name LIKE :{key}")
            values[key] = f"%{word}%"

        query += " AND (" + " OR ".join(name_filters) + ")"

    if in_stock_only:
        query += " AND stock > 0"

    if sort_by in ["name", "price", "stock"]:
        query += f" ORDER BY {sort_by}"

    return await database.fetch_all(query=query, values=values)