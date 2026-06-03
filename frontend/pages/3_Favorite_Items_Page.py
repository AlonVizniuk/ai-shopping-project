import requests
import streamlit as st
from utils.flags import FLAG_IMAGES

st.set_page_config(layout="wide")

BASE_URL = "http://127.0.0.1:8000"

if "token" not in st.session_state:
    st.session_state.token = None

st.title("Favorite Jerseys")

if not st.session_state.token:
    st.error("Please login first")
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state.token}"}

response = requests.get(f"{BASE_URL}/favorite/", headers=headers)

if response.status_code != 200:
    st.error("Failed to load favorites")
    st.stop()

favorites = response.json()

if not favorites:
    st.info("No favorite jerseys yet")
    st.stop()

with st.expander("View items as data frame"):
    public_items = [
        {
            "Jersey": item["name"],
            "Price": item["price"],
            "Stock": item["stock"]
        }
        for item in favorites
    ]
    st.dataframe(public_items, use_container_width=True)

for row_start in range(0, len(favorites), 5):
    columns = st.columns(5)

    for col, item in zip(columns, favorites[row_start:row_start + 5]):
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
                st.write(f"Price: ${item['price']}")
                st.write(f"Stock: {item['stock']}")

                if item["stock"] == 0:
                    st.caption("Status: Out of stock")
                else:
                    st.caption("Status: Available")

                quantity = st.number_input(
                    "Quantity",
                    min_value=1,
                    step=1,
                    key=f"fav_qty_{item['id']}"
                )

                if st.button("Add to Cart", key=f"fav_cart_{item['id']}"):
                    cart_response = requests.post(
                        f"{BASE_URL}/order/item/{item['id']}?quantity={quantity}",
                        headers=headers
                    )

                    if cart_response.status_code == 201:
                        st.success("Added to cart")
                    else:
                        st.error(cart_response.json().get("detail", "Failed to add item"))

                if st.button("♥ Remove Favorite", key=f"fav_remove_{item['id']}"):
                    remove_response = requests.delete(
                        f"{BASE_URL}/favorite/{item['id']}",
                        headers=headers
                    )

                    if remove_response.status_code == 200:
                        st.success("Removed from favorites")
                        st.rerun()
                    else:
                        st.error("Failed to remove favorite")