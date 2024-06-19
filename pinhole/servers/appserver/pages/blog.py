from pinhole.servers.appserver.common import navi, auth

import streamlit as st

st.set_page_config(
    layout='wide',
    page_title='Blog | 观点'
)

navi()
auth()

st.title("Blog | 观点")
