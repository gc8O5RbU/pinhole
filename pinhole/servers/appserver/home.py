from pinhole.servers.appserver.common import navi, auth

import streamlit as st

st.set_page_config(layout='wide')
st.title("Pinhole | 洞见")
st.caption("基于大模型的开源自动化洞察平台")

navi()
auth()

st.markdown("""
>
""")
