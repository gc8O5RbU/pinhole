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
            if cols[1].button("Summary | 简介", key=f"summary-{dref.id}", use_container_width=True):
                display_summary(dref)


@st.experimental_dialog("Summary | 简介", width="large")
def display_summary(dref: DocumentRef) -> None:
    st.subheader(dref.title)
    st.write(dref.date)
    summary = project.get_summary(dref.id)
    if summary is not None:
        st.markdown(summary.content)


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
