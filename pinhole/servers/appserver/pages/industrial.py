from pinhole.servers.appserver.common import project, navi, auth
from pinhole.datasource.document import DocumentRef
from datetime import datetime

from typing import List, Callable

import streamlit as st


def display_documents(title: str, drefs: List[DocumentRef], filt: Callable[[DocumentRef], bool]) -> None:
    has_title: bool = False
    for dref in drefs:
        if filt(dref):
            if not has_title:
                st.markdown(f"### {title}")
                has_title = True

            date = dref.date.strftime("%Y-%m-%d")
            container = st.container()
            container.markdown(f"**[{date}]** (*{dref.publisher}*) {dref.title}")
            cols = st.columns(6)
            cols[0].link_button("Link | 原文", url=dref.url, use_container_width=True)
            cols[1].link_button("Summary | 综述", url=f"/document?id={dref.id}", use_container_width=True)


st.set_page_config(
    layout='wide',
    page_title='Industrial Timeline | 产业信息'
)
st.title("Industrial Timeline | 产业信息")

navi()
auth_state = auth()

docrefs = project.get_document_refs()
docrefs.sort(key=lambda ref: ref.date, reverse=True)
display_documents("Last Week", docrefs, lambda dref: (datetime.today() - dref.date).days <= 7)
display_documents("Last Month", docrefs, lambda dref: 7 < (datetime.today() - dref.date).days <= 30)
