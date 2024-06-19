from pinhole.servers.appserver.common import navi, auth

import streamlit as st

st.set_page_config(layout='wide', page_title="Pinhole | 洞见")
st.title("Pinhole | 洞见")

navi()
auth()

st.markdown("""
我们正处在一个信息爆炸的时代。
""")
