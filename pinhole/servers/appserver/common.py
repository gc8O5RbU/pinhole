from pinhole.project import RemoteProject
from pydantic.dataclasses import dataclass
from os import environ

import math
import streamlit as st


project_port = environ['PINHOLE_API_SERVER_PORT']
project = RemoteProject(f"http://127.0.0.1:{project_port}")
base_path = environ['PINHOLE_APP_SERVER_BASEPATH']


@dataclass
class AuthState:
    logined: bool = False
    username: str = ""
    email: str = ""


@st.cache_resource
def __auth_state() -> AuthState:
    return AuthState(logined=False)


def navi() -> None:
    auth_state = __auth_state()

    with st.sidebar.container():
        st.page_link("home.py", label="Pinhole")
        # st.page_link("pages/ask.py", label="Ask")
        # st.page_link("pages/blog.py", label="Blog")
        st.page_link("pages/academic.py", label="Academic Overview")
        st.page_link("pages/industrial.py", label="Industrial Timeline")

        if auth_state.logined:
            st.page_link("pages/submission.py", label="Submission", use_container_width=True)

        st.divider()


def auth() -> AuthState:
    auth_state: AuthState = __auth_state()

    if auth_state.logined is False:
        with st.sidebar.form("key", border=False):
            email = st.text_input(label='Email')
            password = st.text_input(label='Password', type='password')
            submitted = st.form_submit_button('Login', use_container_width=True)
            if submitted:
                user_ref = project.get_user_ref(email, password)
                if user_ref is not None:
                    auth_state.email = user_ref.email
                    auth_state.username = user_ref.nickname
                    auth_state.logined = True
                    st.rerun()

                st.error("Invalid Username or Password")
    else:
        with st.sidebar.container():
            st.markdown(f"Welcome *{auth_state.username}* 😀")
            if st.button(f"Logout", use_container_width=True):
                auth_state.logined = False
                st.rerun()

    return auth_state


def paginator(item_per_page: int, item_total: int) -> int:
    total_pages = math.ceil(item_total / item_per_page)
    current_page = st.number_input(
        f"Page ({total_pages} in total)",
        min_value=1, max_value=min(1, total_pages),
        step=1
    )
    return int(current_page) - 1
