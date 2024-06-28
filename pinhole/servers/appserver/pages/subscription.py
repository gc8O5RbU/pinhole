from pinhole.servers.appserver.common import navi, auth

import streamlit as st

st.set_page_config(layout='wide', page_title='Subscription | 订阅')
st.title("Subscription | 订阅")

navi()
auth_state = auth()

if auth_state.logined is False:
    st.markdown("*Only available for logined users :(*")
    st.stop()
