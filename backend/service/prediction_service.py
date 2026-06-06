import joblib
import pandas as pd
from repository import favorite_repository, order_repository


model = joblib.load("ml/user_spending_lasso_model.pkl")
scaler = joblib.load("ml/user_spending_scaler.pkl")


async def predict_future_spending(user_id: int):
    favorites = await favorite_repository.get_user_favorites(user_id)
    orders = await order_repository.get_user_orders(user_id)

    closed_orders = [order for order in orders if order["status"] == "CLOSE"]

    favorite_count = len(favorites)
    closed_orders_count = len(closed_orders)

    total_items_purchased = 0
    total_spent = 0

    for order in closed_orders:
        order_items = await order_repository.get_order_items(order["id"])

        for item in order_items:
            total_items_purchased += item["quantity"]

        total_spent += order["total_price"]

    average_order_value = total_spent / closed_orders_count if closed_orders_count > 0 else 0

    input_data = pd.DataFrame([{
        "favorite_count": favorite_count,
        "closed_orders_count": closed_orders_count,
        "total_items_purchased": total_items_purchased,
        "average_order_value": average_order_value,
        "days_since_registration": 30
    }])

    input_scaled = scaler.transform(input_data)
    prediction = model.predict(input_scaled)[0]

    return {
        "favorite_count": favorite_count,
        "closed_orders_count": closed_orders_count,
        "total_items_purchased": total_items_purchased,
        "average_order_value": round(average_order_value, 2),
        "predicted_future_spending": round(max(0, prediction), 2)
    }