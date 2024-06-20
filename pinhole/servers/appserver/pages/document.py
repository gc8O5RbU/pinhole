from pinhole.servers.appserver.common import navi, auth, project


import streamlit as st

try:
    document_id = int(st.query_params.get('id', '-1'))
except Exception:
    document_id = -1

document = project.get_document(document_id)
title = "Unknonw Document" if document is None else f"{document.title}"

st.set_page_config(
    layout='wide',
    page_title=title
)
st.title(title)

navi()
auth()

if document is None:
    st.error(f"query parameter id unspecified or invalid")
    st.stop()

st.link_button("Link | 原文", url=document.url)

summary = project.get_summary_of_document(document_id)
if summary is not None:
    st.markdown("### Summary | 总结")
    st.markdown(summary.content)
