from pinhole.servers.appserver.common import navi, auth, project
from pinhole.datasource.publication import Publication, PublicationRef
from pinhole.datasource.summary import Summary

from typing import List, Callable
from datetime import datetime

import streamlit as st

st.set_page_config(
    layout='wide',
    page_title='Academic Overview | 学术前沿'
)

navi()
auth()


def display_publications(title: str, prefs: List[PublicationRef], filt: Callable[[PublicationRef], bool]) -> None:
    has_title: bool = False
    for pref in prefs:
        if filt(pref):
            if not has_title:
                st.markdown(f"### {title}")
                has_title = True

            date = pref.date.strftime("%Y-%m-%d")
            container = st.container()
            container.markdown(f"**[{date}]** {pref.title}")
            cols = st.columns(6)
            cols[0].link_button("Link | 原文", url=pref.url, use_container_width=True)
            if cols[1].button("Summary | 简介", key=f"summary-{pref.id}", use_container_width=True):
                display_summary(pref)


@st.experimental_dialog("Summary | 简介", width="large")
def display_summary(pref: PublicationRef) -> None:
    st.subheader(pref.title)
    st.write(pref.date)
    summary = project.get_summary_of_publication(pref.id)
    if summary is not None:
        st.markdown(summary.content)


docrefs = project.get_publication_refs()
docrefs.sort(key=lambda ref: ref.date, reverse=True)
display_publications("Yesterday", docrefs, lambda dref: (datetime.today() - dref.date).days <= 1)
display_publications("Last Week", docrefs, lambda dref: 1 < (datetime.today() - dref.date).days <= 7)
display_publications("Last Month", docrefs, lambda dref: 7 < (datetime.today() - dref.date).days <= 30)
