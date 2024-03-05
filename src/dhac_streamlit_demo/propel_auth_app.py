import requests
import streamlit as st
from propelauth_py import UnauthorizedException, init_base_auth
from streamlit.web.server.websocket_headers import _get_websocket_headers


class Auth:
    def __init__(self, auth_url, integration_api_key):
        self.auth = init_base_auth(auth_url, integration_api_key)
        self.auth_url = auth_url
        self.integration_api_key = integration_api_key

    def get_user(self):
        access_token = get_access_token()

        if not access_token:
            return None

        try:
            return self.auth.validate_access_token_and_get_user("Bearer " + access_token)
        except UnauthorizedException as err:
            print("Error validating access token", err)
            return None

    def get_account_url(self):
        return self.auth_url + "/account"

    def logout(self):
        refresh_token = get_refresh_token()
        if not refresh_token:
            return False

        logout_body = {"refresh_token": refresh_token}
        url = f"{self.auth_url}/api/backend/v1/logout"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.integration_api_key,
        }

        response = requests.post(url, json=logout_body, headers=headers)

        return response.ok


def get_access_token():
    return get_cookie("__pa_at")


def get_refresh_token():
    return get_cookie("__pa_rt")


def get_cookie(cookie_name):
    headers = _get_websocket_headers()
    if headers is None:
        return None

    cookies = headers.get("Cookie") or headers.get("cookie") or ""
    for cookie in cookies.split(";"):
        split_cookie = cookie.split("=")
        if len(split_cookie) == 2 and split_cookie[0].strip() == cookie_name:
            return split_cookie[1].strip()

    return None


auth = Auth(
    "https://560282212.propelauthtest.com",
    "e5db4c793b13faf8ae7a1c2b337722bfc63e1e8521c6cd6f2782fb709ec868846e401c688bf3cc07f4881b14eb684ad4",
)

user = auth.get_user()
if user is None:
    st.error("Unauthorized")
    st.stop()

with st.sidebar:
    st.link_button("Account", auth.get_account_url(), use_container_width=True)

st.text("Logged in as " + user.email + " with user ID " + user.user_id)
