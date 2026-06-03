from datetime import datetime
from model.order import Order
from model.order_item import OrderItem
from model.order_status import OrderStatus
from repository import order_repository, item_repository
from exceptions.exception import item_out_of_stock_exception


def build_order(order_record) -> Order:
    return Order(
        id=order_record["id"],
        user_id=order_record["user_id"],
        order_date=order_record["order_date"],
        shipping_address=order_record["shipping_address"],
        total_price=order_record["total_price"],
        status=OrderStatus(order_record["status"])
    )


async def add_item_to_order(user_id: int, item_id: int, quantity: int, shipping_address: str):
    item = await item_repository.get_item_by_id(item_id)

    if not item:
        return None

    if quantity > item["stock"]:
        raise item_out_of_stock_exception()

    temp_order = await order_repository.get_temp_order_by_user_id(user_id)

    if not temp_order:
        order = Order(user_id=user_id, order_date=datetime.utcnow(), shipping_address=shipping_address, total_price=0, status=OrderStatus.TEMP)
        temp_order = await order_repository.create_order(order)

    order_item = OrderItem(order_id=temp_order["id"], item_id=item_id, quantity=quantity, price_per_item=item["price"])
    existing_order_item = await order_repository.get_order_item(temp_order["id"], item_id)

    if existing_order_item:
        new_quantity = existing_order_item["quantity"] + quantity
        if new_quantity > item["stock"]:
            raise item_out_of_stock_exception()
        await order_repository.update_order_item_quantity(temp_order["id"], item_id, new_quantity)
    else:
        await order_repository.add_order_item(order_item)

    items = await order_repository.get_order_items(temp_order["id"])
    total_price = sum(order_item["quantity"] * order_item["price_per_item"] for order_item in items)
    await order_repository.update_order_total(temp_order["id"], total_price)
    return build_order(await order_repository.get_order_by_id(temp_order["id"]))


async def get_order_items(user_id: int):
    temp_order = await order_repository.get_temp_order_by_user_id(user_id)
    if not temp_order:
        return []
    return await order_repository.get_order_items(temp_order["id"])


async def remove_item_from_order(user_id: int, item_id: int):
    temp_order = await order_repository.get_temp_order_by_user_id(user_id)

    if not temp_order:
        return None

    await order_repository.remove_order_item(temp_order["id"], item_id)
    items = await order_repository.get_order_items(temp_order["id"])

    if not items:
        await order_repository.delete_order(temp_order["id"])
        return {"message": "Order deleted because it has no items"}

    total_price = sum(item["quantity"] * item["price_per_item"] for item in items)
    await order_repository.update_order_total(temp_order["id"], total_price)
    return build_order(await order_repository.get_order_by_id(temp_order["id"]))


async def purchase_order(user_id: int):
    temp_order = await order_repository.get_temp_order_by_user_id(user_id)

    if not temp_order:
        return None

    order_items = await order_repository.get_order_items(temp_order["id"])

    for order_item in order_items:
        item = await item_repository.get_item_by_id(order_item["item_id"])
        new_stock = item["stock"] - order_item["quantity"]

        if new_stock < 0:
            raise item_out_of_stock_exception()
        await item_repository.update_item_stock(order_item["item_id"], new_stock)

    await order_repository.close_order(temp_order["id"])
    return {"message": "Order purchased successfully"}


async def get_user_orders(user_id: int):
    orders = await order_repository.get_user_orders(user_id)
    return [build_order(order) for order in orders]


async def get_order_by_id(user_id: int, order_id: int):
    order = await order_repository.get_order_by_id(order_id)
    if not order or order["user_id"] != user_id:
        return None
    items = await order_repository.get_order_items(order_id)
    return {"order": build_order(order), "items": items}


async def delete_temp_order(user_id: int):
    temp_order = await order_repository.get_temp_order_by_user_id(user_id)

    if not temp_order:
        return None

    await order_repository.delete_order_items_by_order_id(temp_order["id"])
    await order_repository.delete_order(temp_order["id"])
    return True


async def update_order_item_quantity(user_id: int, item_id: int, quantity: int):
    temp_order = await order_repository.get_temp_order_by_user_id(user_id)

    if not temp_order:
        return None

    item = await item_repository.get_item_by_id(item_id)

    if not item:
        return None

    if quantity > item["stock"]:
        raise item_out_of_stock_exception()

    await order_repository.update_order_item_quantity(temp_order["id"], item_id, quantity)
    items = await order_repository.get_order_items(temp_order["id"])
    total_price = sum(order_item["quantity"] * order_item["price_per_item"] for order_item in items)
    await order_repository.update_order_total(temp_order["id"], total_price)
    return build_order(await order_repository.get_order_by_id(temp_order["id"]))