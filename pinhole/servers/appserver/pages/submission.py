from pinhole.servers.appserver.common import navi, auth

import streamlit as st

st.set_page_config(layout='wide', page_title='Submission | 投稿')
st.title("Submission | 投稿")

navi()
auth_state = auth()

if auth_state.logined is False:
    st.markdown("*Only available for subscribed users :(*")
    st.stop()
