import streamlit as st
from utils.http_client import get_session

st.set_page_config(layout="wide")

BASE_URL = "http://127.0.0.1:8000"

session = get_session()

if "token" not in st.session_state:
    st.session_state.token = None

st.title("Future Spending Prediction")

if not st.session_state.token:
    st.warning("Please login first")
    st.stop()

headers = {
    "Authorization": f"Bearer {st.session_state.token}"
}

response = session.get(
    f"{BASE_URL}/prediction/future-spending",
    headers=headers
)

if response.status_code != 200:
    st.error("Prediction service is not available")
    st.stop()

data = response.json()

st.subheader("User Shopping Statistics")

st.write(f"Favorite Items: {data['favorite_count']}")
st.write(f"Closed Orders: {data['closed_orders_count']}")
st.write(f"Purchased Items: {data['total_items_purchased']}")
st.write(f"Average Order Value: ${data['average_order_value']}")

st.divider()

st.metric(
    "Estimated Future Spending",
    f"${data['predicted_future_spending']}"
)
