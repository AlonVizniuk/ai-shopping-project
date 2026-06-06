import random
import pandas as pd

rows = []

for user_id in range(1, 1001):
    favorite_count = random.randint(0, 20)
    closed_orders_count = random.randint(0, 12)
    total_items_purchased = random.randint(0, 40)

    if closed_orders_count == 0 or total_items_purchased == 0:
        average_order_value = 0
        closed_orders_count = 0
        total_items_purchased = 0
    else:
        average_order_value = random.randint(50, 180)

    days_since_registration = random.randint(1, 365)

    future_spending = (
        favorite_count * 8
        + closed_orders_count * 65
        + total_items_purchased * 12
        + average_order_value * 1.7
        + days_since_registration * 0.2
        + random.randint(-40, 40)
    )

    future_spending = max(0.0, round(future_spending, 2))

    rows.append({
        "user_id": user_id,
        "favorite_count": favorite_count,
        "closed_orders_count": closed_orders_count,
        "total_items_purchased": total_items_purchased,
        "average_order_value": average_order_value,
        "days_since_registration": days_since_registration,
        "future_spending": future_spending
    })

df = pd.DataFrame(rows)
df.to_csv("ml/user_spending_dataset.csv", index=False)

print("Dataset created successfully")