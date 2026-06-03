from model.item import Item
from repository import item_repository
import json
from repository import cache_repository


def build_item(item_record) -> Item:
    return Item(
        id=item_record["id"],
        name=item_record["name"],
        price=item_record["price"],
        stock=item_record["stock"]
    )


async def create_item(item: Item):
    created_item = await item_repository.create_item(item)
    cache_repository.remove_cache_entity("items")
    return build_item(created_item)


async def get_item_by_id(item_id: int):
    item = await item_repository.get_item_by_id(item_id)
    if not item:
        return None
    return build_item(item)


async def get_items():
    cache_key = "items"
    cached_items = cache_repository.get_cache_entity(cache_key)

    if cached_items:
        return json.loads(cached_items)

    items = await item_repository.get_items()
    response = [build_item(item).dict() for item in items]
    cache_repository.create_cache_entity(cache_key, json.dumps(response))
    return response


async def delete_item(item_id: int):
    item = await item_repository.get_item_by_id(item_id)
    if not item:
        return None
    await item_repository.delete_item(item_id)
    cache_repository.remove_cache_entity("items")
    return build_item(item)


async def update_item_stock(item_id: int, stock: int):
    item = await item_repository.get_item_by_id(item_id)
    if not item:
        return None
    updated_item = await item_repository.update_item_stock(item_id, stock)
    cache_repository.remove_cache_entity("items")
    return build_item(updated_item)


async def search_items_by_name(name: str):
    items = await item_repository.search_items_by_name(name)
    return [build_item(item) for item in items]


async def search_items_by_price(operator: str, price: float):
    if operator not in [">", "<", "="]:
        return None
    items = await item_repository.search_items_by_price(operator, price)
    return [build_item(item) for item in items]


async def search_items(
        name: str = "",
        min_price: float = 0,
        max_price: float = 999999,
        min_stock: int = 0,
        max_stock: int = 999999,
        in_stock_only: bool = False,
        sort_by: str = "name"
):
    items = await item_repository.search_items(
        name,
        min_price,
        max_price,
        min_stock,
        max_stock,
        in_stock_only,
        sort_by
    )

    return [build_item(item) for item in items]