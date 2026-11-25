import os
import requests
import streamlit as st
from dotenv import load_dotenv

# Load frontend env
load_dotenv()

BACKEND_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000")

def get_headers():
    """Retrieve Authorization headers containing active JWT token."""
    headers = {}
    if "token" in st.session_state and st.session_state["token"]:
        headers["Authorization"] = f"Bearer {st.session_state['token']}"
    return headers


def register_user(username, email, password):
    """Post registration request to API."""
    url = f"{BACKEND_URL}/api/auth/register"
    payload = {"username": username, "email": email, "password": password}
    try:
        res = requests.post(url, json=payload)
        return res
    except Exception as e:
        st.error(f"Connection failed: {e}")
        return None


def login_user(username, password):
    """Post login request to API."""
    url = f"{BACKEND_URL}/api/auth/login"
    payload = {"username": username, "password": password}
    try:
        # OAuth2 password flow expects form data
        res = requests.post(url, data=payload)
        return res
    except Exception as e:
        st.error(f"Connection failed: {e}")
        return None


def get_request(endpoint):
    """Authenticated GET request."""
    url = f"{BACKEND_URL}{endpoint}"
    try:
        res = requests.get(url, headers=get_headers())
        return res
    except Exception as e:
        st.error(f"Connection failed: {e}")
        return None


def post_request(endpoint, json_data=None):
    """Authenticated POST request."""
    url = f"{BACKEND_URL}{endpoint}"
    try:
        res = requests.post(url, json=json_data, headers=get_headers())
        return res
    except Exception as e:
        st.error(f"Connection failed: {e}")
        return None


def post_file_request(endpoint, file_bytes, file_name):
    """Authenticated POST request for file uploads."""
    url = f"{BACKEND_URL}{endpoint}"
    files = {"file": (file_name, file_bytes, "application/pdf")}
    try:
        res = requests.post(url, files=files, headers=get_headers())
        return res
    except Exception as e:
        st.error(f"Connection failed: {e}")
        return None
