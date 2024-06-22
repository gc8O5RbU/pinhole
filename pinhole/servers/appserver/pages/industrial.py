from pinhole.servers.appserver.common import project, navi, auth, paginator
from pinhole.datasource.document import DocumentRef
from datetime import datetime

from typing import List, Callable

import streamlit as st


st.set_page_config(
    layout='wide',
    page_title='Industrial Timeline | 产业信息'
)
st.title("Industrial Timeline | 产业信息")

navi()
auth_state = auth()


def display_documents(drefs: List[DocumentRef]) -> None:
    for dref in drefs:
        date = dref.date.strftime("%Y-%m-%d")
        cols = st.columns([4, 1, 1])
        cols[0].markdown(f"**[{date}]** (*{dref.publisher}*) {dref.title}")
        cols[1].link_button("Link | 原文", url=dref.url, use_container_width=True)
        cols[2].link_button("Summary | 综述", url=f"/document?id={dref.id}", use_container_width=True)


docrefs = project.get_document_refs()
docrefs.sort(key=lambda ref: ref.date, reverse=True)
item_per_page = 10

cols = st.columns([3, 1])
keywords = [kw.lower() for kw in cols[0].text_input(label="Search by keyword").split()]

if len(keywords) > 0:
    matched_docrefs: List[DocumentRef] = []
    for dref in docrefs:
        title = dref.title.lower()
        for kw in keywords:
            if kw in title:
                matched_docrefs.append(dref)
                break

    docrefs = matched_docrefs

with cols[1]:
    page = paginator(item_per_page, len(docrefs))

display_documents(docrefs[page * item_per_page:(page + 1) * item_per_page])
