from config.database import database
from model.order import Order
from model.order_item import OrderItem


async def get_temp_order_by_user_id(user_id: int):
    query = "SELECT * FROM orders WHERE user_id = :user_id AND status = 'TEMP'"
    return await database.fetch_one(query=query, values={"user_id": user_id})


async def create_order(order: Order):
    query = """
        INSERT INTO orders (user_id, order_date, shipping_address, total_price, status)
        VALUES (:user_id, :order_date, :shipping_address, :total_price, :status)
    """
    values = {
        "user_id": order.user_id,
        "order_date": order.order_date,
        "shipping_address": order.shipping_address,
        "total_price": order.total_price,
        "status": order.status.name
    }
    await database.execute(query=query, values=values)
    created_id = await database.fetch_val(query="SELECT LAST_INSERT_ID()")
    return await get_order_by_id(created_id)


async def get_order_by_id(order_id: int):
    query = "SELECT * FROM orders WHERE id = :order_id"
    return await database.fetch_one(query=query, values={"order_id": order_id})


async def add_order_item(order_item: OrderItem):
    query = """
        INSERT INTO order_items (order_id, item_id, quantity, price_per_item)
        VALUES (:order_id, :item_id, :quantity, :price_per_item)
    """
    values = {
        "order_id": order_item.order_id,
        "item_id": order_item.item_id,
        "quantity": order_item.quantity,
        "price_per_item": order_item.price_per_item
    }
    await database.execute(query=query, values=values)


async def get_order_item(order_id: int, item_id: int):
    query = "SELECT * FROM order_items WHERE order_id = :order_id AND item_id = :item_id"
    return await database.fetch_one(query=query, values={"order_id": order_id, "item_id": item_id})


async def update_order_item_quantity(order_id: int, item_id: int, quantity: int):
    query = """
        UPDATE order_items
        SET quantity = :quantity
        WHERE order_id = :order_id AND item_id = :item_id
    """
    values = {
        "order_id": order_id,
        "item_id": item_id,
        "quantity": quantity
    }
    await database.execute(query=query, values=values)


async def get_order_items(order_id: int):
    query = """
        SELECT order_items.*, items.name
        FROM order_items
        JOIN items ON order_items.item_id = items.id
        WHERE order_items.order_id = :order_id
    """
    return await database.fetch_all(query=query, values={"order_id": order_id})


async def update_order_total(order_id: int, total_price: float):
    query = "UPDATE orders SET total_price = :total_price WHERE id = :order_id"
    return await database.execute(query=query, values={"order_id": order_id, "total_price": total_price})


async def remove_order_item(order_id: int, item_id: int):
    query = "DELETE FROM order_items WHERE order_id = :order_id AND item_id = :item_id"
    return await database.execute(query=query, values={"order_id": order_id, "item_id": item_id})


async def delete_order(order_id: int):
    query = "DELETE FROM orders WHERE id = :order_id"
    return await database.execute(query=query, values={"order_id": order_id})


async def close_order(order_id: int):
    query = "UPDATE orders SET status = 'CLOSE' WHERE id = :order_id"
    return await database.execute(query=query, values={"order_id": order_id})


async def get_user_orders(user_id: int):
    query = """
        SELECT *
        FROM orders
        WHERE user_id = :user_id
        ORDER BY
            CASE WHEN status = 'TEMP' THEN 0 ELSE 1 END,
            order_date DESC
    """
    return await database.fetch_all(query=query, values={"user_id": user_id})


async def delete_order_items_by_order_id(order_id: int):
    query = "DELETE FROM order_items WHERE order_id = :order_id"
    await database.execute(query=query, values={"order_id": order_id})