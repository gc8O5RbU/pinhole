from markdownify import markdownify as md  # type: ignore
from loguru import logger

from tempfile import mktemp
from typing import Optional
from os import remove

import pymupdf  # type: ignore
import requests


def load_arxiv_content(arxiv_id: str) -> Optional[str]:
    html_addr = f"https://arxiv.org/html/{arxiv_id}"
    pdf_addr = f"https://arxiv.org/pdf/{arxiv_id}"

    resp = requests.get(html_addr)

    if resp.status_code == 404:
        pdf_resp = requests.get(pdf_addr)
        if pdf_resp.status_code != 200:
            logger.warning(f"http error {pdf_resp.status_code} when fetching arxiv document {arxiv_id} in pdf format")
            return None

        pdf_file = mktemp(suffix='.pdf')
        with open(pdf_file, 'wb') as f:
            f.write(pdf_resp.content)

        content = ""
        for page in pymupdf.open(pdf_file):
            content += page.get_text() + "\n"

        remove(pdf_file)
        return content
    elif resp.status_code != 200:
        logger.warning(f"http error {resp.status_code} when fetching arxiv document {arxiv_id} in html format")
        return None
    else:
        content = md(resp.text)
        if content is None:
            logger.warning(f"failed to tranfer html to markdown for {arxiv_id}")

        return content
