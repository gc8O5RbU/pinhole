from pinhole.servers.appserver.common import navi, auth
import streamlit as st

st.set_page_config(
    layout='wide',
    page_title='Academic Overview | 学术前沿'
)

navi()
auth()
