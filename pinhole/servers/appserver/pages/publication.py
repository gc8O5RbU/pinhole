from pinhole.servers.appserver.common import navi, auth, project
from pinhole.datasource.publication import Publication, PublicationRef
from pinhole.datasource.summary import Summary

from typing import List, Callable
from datetime import datetime

import streamlit as st

try:
    publication_id = int(st.query_params.get('id', '-1'))
except Exception:
    publication_id = -1

publication = project.get_publication(publication_id)
title = "Unknonw Publication" if publication is None else f"{publication.title}"

st.set_page_config(
    layout='wide',
    page_title=title
)
st.title(title)

navi()
auth()

if publication is None:
    st.error(f"query parameter id unspecified or invalid")
    st.stop()

st.link_button("Link | 原文", url=publication.url)

summary = project.get_summary_of_publication(publication_id)
if summary is not None:
    st.markdown("### Summary | 总结")
    st.markdown(summary.content)
else:
    st.markdown("### Abstract | 摘要")
    st.write(publication.abstract)
