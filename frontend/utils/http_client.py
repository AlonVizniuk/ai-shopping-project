import requests
import streamlit as st


@st.cache_resource
def get_session():
    return requests.Session()