from pinhole.servers.appserver.common import navi, auth, project, base_path, paginator
from pinhole.datasource.publication import Publication, PublicationRef
from pinhole.datasource.summary import Summary

from typing import List, Callable
from datetime import datetime

import streamlit as st


st.set_page_config(
    layout='wide',
    page_title='Academic Overview | 学术前沿'
)
st.title('Academic Overview | 学术前沿')

navi()
auth_state = auth()


def display_publications(prefs: List[PublicationRef]) -> None:
    for pref in prefs:
        date = pref.date.strftime("%Y-%m-%d")
        cols = st.columns([4, 1, 1])
        cols[0].markdown(f"**[{date}]** {pref.title}")
        cols[1].link_button("Link | 原文", url=pref.url, use_container_width=True)
        cols[2].link_button("Summary | 综述", url=f"{base_path}/publication?id={pref.id}", use_container_width=True)


prefs = project.get_publication_refs()
prefs.sort(key=lambda ref: ref.date, reverse=True)
item_per_page = 10

cols = st.columns([3, 1])
keywords = [kw.lower() for kw in cols[0].text_input(label="Search by keyword").split()]

if len(keywords) > 0:
    matched_prefs: List[PublicationRef] = []
    for pref in prefs:
        title = pref.title.lower()
        for kw in keywords:
            if kw in title:
                matched_prefs.append(pref)
                break

    prefs = matched_prefs

with cols[1]:
    page = paginator(item_per_page, len(prefs))

display_publications(prefs[page * item_per_page:(page + 1) * item_per_page])
