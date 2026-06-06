import streamlit as st
from utils.http_client import get_session

st.set_page_config(layout="wide")

BASE_URL = "http://127.0.0.1:8000"

session = get_session()

if "token" not in st.session_state:
    st.session_state.token = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "prompts_left" not in st.session_state:
    st.session_state.prompts_left = 5

st.title("Chat Assistant")
st.caption("Ask questions about available jerseys, prices, stock, and recommendations")

if not st.session_state.token:
    st.error("Please login first")
    st.stop()

st.info(f"Prompts left: {st.session_state.prompts_left}")

col1, col2 = st.columns(2)

with col1:
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

with col2:
    st.caption("The assistant can answer questions about products and website usage.")

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

prompt = st.chat_input("Ask the shopping assistant")

if prompt:
    headers = {"Authorization": f"Bearer {st.session_state.token}"}

    with st.chat_message("user"):
        st.write(prompt)

    response = session.post(
        f"{BASE_URL}/chat/",
        json={"prompt": prompt},
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()

        st.session_state.chat_history.append({
            "role": "user",
            "content": prompt
        })

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": data["answer"]
        })

        st.session_state.prompts_left = data["prompts_left"]

        with st.chat_message("assistant"):
            st.write(data["answer"])

        st.rerun()
    else:
        try:
            error_message = response.json().get("detail", "Chat assistant is not available")
        except ValueError:
            error_message = "Chat assistant is not available"

        st.error(error_message)