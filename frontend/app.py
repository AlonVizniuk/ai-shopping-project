import streamlit as st
from utils.http_client import get_session

st.set_page_config(page_title="World Cup Jersey Store", layout="wide")

BASE_URL = "http://127.0.0.1:8000"

session = get_session()

if "token" not in st.session_state:
    st.session_state.token = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "prompts_left" not in st.session_state:
    st.session_state.prompts_left = 5

if "login_success" not in st.session_state:
    st.session_state.login_success = False

st.title("World Cup Jersey Store")
st.caption("Login, register, and manage your shopping account")

with st.sidebar:
    st.header("Account")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        response = session.post(
            f"{BASE_URL}/auth/token",
            data={"username": username, "password": password}
        )

        if response.status_code == 200:
            st.session_state.token = response.json()["jwt_token"]

            headers = {
                "Authorization": f"Bearer {st.session_state.token}"
            }

            session.delete(f"{BASE_URL}/chat/", headers=headers)

            st.session_state.chat_history = []
            st.session_state.prompts_left = 5
            st.session_state.login_success = True

            st.rerun()

        else:
            st.error("Login failed")

    if st.session_state.login_success:
        st.success("Logged in successfully")
        st.session_state.login_success = False

    if st.button("Logout"):
        if st.session_state.token:
            headers = {
                "Authorization": f"Bearer {st.session_state.token}"
            }

            session.delete(f"{BASE_URL}/chat/", headers=headers)

        st.session_state.token = None
        st.session_state.chat_history = []
        st.session_state.prompts_left = 5

        st.success("Logged out")

    st.divider()

    if st.button("Delete My Account"):
        if not st.session_state.token:
            st.error("Please login first")

        else:
            headers = {
                "Authorization": f"Bearer {st.session_state.token}"
            }

            response = session.delete(
                f"{BASE_URL}/user/me",
                headers=headers
            )

            if response.status_code == 200:
                st.session_state.token = None
                st.session_state.chat_history = []
                st.session_state.prompts_left = 5

                st.success("Account deleted successfully")

            else:
                st.error(response.json().get("detail", "Failed to delete account"))

    st.divider()

    st.info("Use the pages menu to navigate the store.")

st.subheader("Create New Account")

with st.form("register_form"):
    col1, col2 = st.columns(2)

    with col1:
        first_name = st.text_input("First name")
        last_name = st.text_input("Last name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")

    with col2:
        country = st.text_input("Country")
        city = st.text_input("City")
        new_username = st.text_input("New username")
        new_password = st.text_input("New password", type="password")

    submitted = st.form_submit_button("Create Account")

    if submitted:
        if not all([first_name, last_name, email, phone, country, city, new_username, new_password]):
            st.error("Please fill all fields")

        else:
            user_data = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": phone,
                "country": country,
                "city": city,
                "username": new_username,
                "password": new_password
            }

            response = session.post(
                f"{BASE_URL}/user/",
                json=user_data
            )

            if response.status_code == 201:
                st.success("Account created successfully. You can now login from the sidebar.")

            else:
                st.error(response.json().get("detail", "Failed to create account"))