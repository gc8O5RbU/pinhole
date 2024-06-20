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
            cols[1].link_button("Summary | 综述", url=f"/publication?id={pref.id}", use_container_width=True)


docrefs = project.get_publication_refs()
docrefs.sort(key=lambda ref: ref.date, reverse=True)
display_publications("Yesterday", docrefs, lambda dref: (datetime.today() - dref.date).days <= 1)
display_publications("Last Week", docrefs, lambda dref: 1 < (datetime.today() - dref.date).days <= 7)
