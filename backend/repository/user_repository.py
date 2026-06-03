from config.database import database
from model.user import User


async def get_user_by_id(user_id: int):
    query ="SELECT * FROM users WHERE id = :user_id"
    return await database.fetch_one(query=query, values={"user_id": user_id})


async def get_user_by_username(username: str):
    query = "SELECT * FROM users WHERE username = :username"
    return await database.fetch_one(query=query, values={"username": username})


async def create_user(user_request, hashed_password: str):
    query = """
        INSERT INTO users (
            first_name,
            last_name,
            email,
            phone,
            country,
            city,
            username,
            hashed_password
        )
        VALUES (
            :first_name,
            :last_name,
            :email,
            :phone,
            :country,
            :city,
            :username,
            :hashed_password
        )
    """

    values = {
        "first_name": user_request.first_name,
        "last_name": user_request.last_name,
        "email": user_request.email,
        "phone": user_request.phone,
        "country": user_request.country,
        "city": user_request.city,
        "username": user_request.username,
        "hashed_password": hashed_password
    }

    await database.execute(query=query, values=values)
    created_id = await database.fetch_val(query="SELECT LAST_INSERT_ID()")
    return await get_user_by_id(created_id)


async def get_users():
    query = "SELECT * FROM users"
    return await database.fetch_all(query=query)


async def delete_user(user_id: int):
    user_orders = await database.fetch_all(
        query="SELECT id FROM orders WHERE user_id = :user_id",
        values={"user_id": user_id}
    )

    for order in user_orders:
        await database.execute(
            query="DELETE FROM order_items WHERE order_id = :order_id",
            values={"order_id": order["id"]}
        )

    await database.execute(
        query="DELETE FROM orders WHERE user_id = :user_id",
        values={"user_id": user_id}
    )

    await database.execute(
        query="DELETE FROM favorite_items WHERE user_id = :user_id",
        values={"user_id": user_id}
    )

    await database.execute(
        query="DELETE FROM users WHERE id = :user_id",
        values={"user_id": user_id}
    )


async def get_user_by_email(email: str):
    query = "SELECT * FROM users WHERE email = :email"
    return await database.fetch_one(query=query, values={"email": email})