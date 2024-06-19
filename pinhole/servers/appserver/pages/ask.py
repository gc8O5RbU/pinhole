from pinhole.servers.appserver.common import navi, auth

import streamlit as st

st.set_page_config(
    layout='wide',
    page_title='Ask Pinhole | 探索'
)

navi()
auth()

st.title("Ask Pinhole | 探索")
