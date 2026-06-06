import streamlit as st
from utils.http_client import get_session
from utils.flags import FLAG_IMAGES

st.set_page_config(layout="wide")

BASE_URL = "http://127.0.0.1:8000"

session = get_session()

@st.cache_data(ttl=30)
def get_cached_items():
    res = session.get(f"{BASE_URL}/item/")
    return res.json()

if "token" not in st.session_state:
    st.session_state.token = None

if "filters_applied" not in st.session_state:
    st.session_state.filters_applied = False

st.title("World Cup Jersey Store")
st.caption("Find your favorite national team jersey")

search_name = st.text_input("Search jerseys", placeholder="Argentina, Brazil, France...")

with st.expander("Filters"):
    col1, col2 = st.columns(2)

    with col1:
        min_price = st.number_input("Min price", min_value=0.0, step=1.0)
        min_stock = st.number_input("Min stock", min_value=0, step=1)

    with col2:
        max_price = st.number_input("Max price", min_value=0.0, value=999999.0, step=1.0)
        max_stock = st.number_input("Max stock", min_value=0, value=999999, step=1)

    in_stock_only = st.checkbox("Show only available jerseys")
    sort_by = st.selectbox("Sort by", ["name", "price", "stock"])

if st.button("Apply Search"):
    st.session_state.filters_applied = True

if st.button("Clear Search"):
    st.session_state.filters_applied = False

if st.session_state.filters_applied:
    response = session.get(
        f"{BASE_URL}/item/search/filter",
        params={
            "name": search_name,
            "min_price": min_price,
            "max_price": max_price,
            "min_stock": min_stock,
            "max_stock": max_stock,
            "in_stock_only": in_stock_only,
            "sort_by": sort_by
        }
    )

    if response.status_code != 200:
        st.error("Failed to load items")
        st.stop()

    items = response.json()

else:
    items = get_cached_items()

if not items:
    st.info("No jerseys found")
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else None

favorite_ids = set()

if headers:
    favorites_response = session.get(f"{BASE_URL}/favorite/", headers=headers)

    if favorites_response.status_code == 200:
        favorite_ids = {item["id"] for item in favorites_response.json()}

st.subheader("Available Jerseys")

with st.expander("View items as data frame"):
    public_items = [
        {
            "Jersey": item["name"],
            "Price": item["price"],
            "Stock": item["stock"]
        }
        for item in items
    ]
    st.dataframe(public_items, use_container_width=True)

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
                st.write(f"Price: ${item['price']}")
                st.write(f"Stock: {item['stock']}")

                st.caption("Status: Out of stock" if item["stock"] == 0 else "Status: Available")

                quantity = st.number_input(
                    "Quantity",
                    min_value=1,
                    step=1,
                    key=f"qty_{item['id']}"
                )

                if st.button(
                    "Add to Cart",
                    key=f"cart_{item['id']}",
                    disabled=item["stock"] == 0
                ):
                    if not headers:
                        st.error("Please login first")
                    else:
                        cart_response = session.post(
                            f"{BASE_URL}/order/item/{item['id']}?quantity={quantity}",
                            headers=headers
                        )

                        if cart_response.status_code == 201:
                            st.success("Added to cart")
                        else:
                            st.error(cart_response.json().get("detail", "Failed to add item"))

                is_favorite = item["id"] in favorite_ids
                favorite_label = "♥ Favorite" if is_favorite else "♡ Favorite"

                if st.button(favorite_label, key=f"fav_toggle_{item['id']}"):
                    if not headers:
                        st.error("Please login first")
                    else:
                        if is_favorite:
                            fav_response = session.delete(
                                f"{BASE_URL}/favorite/{item['id']}",
                                headers=headers
                            )

                            if fav_response.status_code == 200:
                                st.success("Removed from favorites")
                                st.rerun()
                            else:
                                st.error("Failed to remove favorite")
                        else:
                            fav_response = session.post(
                                f"{BASE_URL}/favorite/{item['id']}",
                                headers=headers
                            )

                            if fav_response.status_code == 201:
                                st.success("Added to favorites")
                                st.rerun()
                            else:
                                st.error(fav_response.json().get("detail", "Failed to add favorite"))