import streamlit as st
from utils.http_client import get_session
from utils.flags import FLAG_IMAGES

st.set_page_config(layout="wide")

BASE_URL = "http://127.0.0.1:8000"

session = get_session()

if "token" not in st.session_state:
    st.session_state.token = None

st.title("Order Page")

if not st.session_state.token:
    st.error("Please login first")
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state.token}"}


def get_order_details(order_id: int):
    res = session.get(f"{BASE_URL}/order/{order_id}", headers=headers)
    return res.json() if res.status_code == 200 else None


def show_items_grid(items, editable: bool):
    if not items:
        st.info("No items in this order")
        return

    for row_start in range(0, len(items), 5):
        columns = st.columns(5)

        for col, item in zip(columns, items[row_start:row_start + 5]):
            with col:
                with st.container(border=True):
                    country_name = item["name"].replace(" Jersey", "").lower()
                    flag_url = FLAG_IMAGES.get(country_name)

                    if flag_url:
                        st.markdown(
                            f"""
                            <div style="
                                height:120px;
                                background-image:url('{flag_url}');
                                background-size:cover;
                                background-position:center;
                                border-radius:10px;
                            "></div>
                            """,
                            unsafe_allow_html=True
                        )

                    st.markdown(f"### {item['name'].title()}")
                    st.write(f"Quantity: {item['quantity']}")

                    current_stock = item["quantity"]

                    item_response = session.get(f"{BASE_URL}/item/{item['item_id']}")

                    if item_response.status_code == 200:
                        current_item = item_response.json()
                        current_stock = current_item["stock"]

                        if item["quantity"] > current_stock:
                            st.warning(f"Only {current_stock} left in stock. Please update or remove this item.")

                    st.write(f"Price per item: ${item['price_per_item']}")
                    st.write(f"Total: ${item['quantity'] * item['price_per_item']}")

                    if editable:
                        new_quantity = st.number_input(
                            "Edit quantity",
                            min_value=1,
                            max_value=max(current_stock, 1),
                            value=min(item["quantity"], max(current_stock, 1)),
                            step=1,
                            key=f"edit_qty_{item['item_id']}"
                        )

                        if st.button("Update Quantity", key=f"update_qty_{item['item_id']}"):
                            res = session.put(
                                f"{BASE_URL}/order/item/{item['item_id']}/quantity?quantity={new_quantity}",
                                headers=headers
                            )

                            if res.status_code == 200:
                                st.success("Quantity updated")
                                st.rerun()
                            else:
                                st.error(res.json().get("detail", "Failed to update quantity"))

                        if st.button("Remove from order", key=f"remove_{item['item_id']}"):
                            res = session.delete(
                                f"{BASE_URL}/order/item/{item['item_id']}",
                                headers=headers
                            )

                            if res.status_code == 200:
                                st.success("Item removed")
                                st.rerun()
                            else:
                                st.error("Failed to remove item")


orders_response = session.get(f"{BASE_URL}/order/", headers=headers)

if orders_response.status_code != 200:
    st.error("Failed to load orders")
    st.stop()

orders = orders_response.json()

if not orders:
    st.info("No orders found")
    st.stop()

temp_orders = [order for order in orders if order["status"] == "TEMP"]
closed_orders = [order for order in orders if order["status"] == "CLOSE"]

st.subheader("Pending Order")

if temp_orders:
    temp_order = temp_orders[0]
    temp_data = get_order_details(temp_order["id"])

    if temp_data:
        temp_items = temp_data["items"]

        with st.container(border=True):
            st.write(f"Shipping address: {temp_order['shipping_address']}")
            st.write(f"Total price: ${temp_order['total_price']}")

            st.markdown("### Items")
            show_items_grid(temp_items, editable=True)

            if st.button("Purchase Order"):
                response = session.put(f"{BASE_URL}/order/purchase", headers=headers)

                if response.status_code == 200:
                    st.success("Order purchased successfully")
                    st.rerun()
                else:
                    st.error(response.json().get("detail", "Purchase failed"))

            if st.button("Delete Pending Order"):
                response = session.delete(f"{BASE_URL}/order/temp", headers=headers)

                if response.status_code == 200:
                    st.success("Pending order deleted")
                    st.rerun()
                else:
                    st.error("Failed to delete order")

else:
    st.info("No pending order")

st.subheader("Closed Orders")

if closed_orders:
    for order in closed_orders:
        with st.container(border=True):
            st.markdown(f"### Order #{order['id']}")
            st.write(f"Date: {order['order_date'][:10]}")
            st.write(f"Total price: ${order['total_price']}")
            st.write(f"Shipping address: {order['shipping_address']}")

            if st.button("View Details", key=f"closed_details_{order['id']}"):
                st.session_state.selected_closed_order_id = order["id"]

    if "selected_closed_order_id" in st.session_state:
        closed_data = get_order_details(st.session_state.selected_closed_order_id)

        if closed_data:
            st.markdown("---")
            st.subheader(f"Order #{st.session_state.selected_closed_order_id} Details")
            show_items_grid(closed_data["items"], editable=False)
else:
    st.info("No closed orders yet")