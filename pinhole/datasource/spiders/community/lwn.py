from pinhole.datasource.spider import PinholeScrapySpider
from pinhole.datasource.document import Document

from scrapy.http import Request, FormRequest  # type: ignore
from scrapy.responsetypes import Response  # type: ignore
from markdownify import markdownify as md  # type: ignore

from os import environ
from datetime import datetime
from typing import Any, List, Dict
from loguru import logger

import dateparser


class LwnHeadline(PinholeScrapySpider):

    start_urls = ["https://lwn.net/headlines/text"]
    channels = set(['Kernel', 'Security'])

    def __init__(self, **kwargs) -> None:
        super(LwnHeadline, self).__init__(**kwargs)

        self.temp_documents: Dict[str, Document] = {}

    def start_requests(self):
        login_url = "https://lwn.net/Login/"
        lwn_username = environ.get("PINHOLE_LWN_USERNAME", "").strip()
        lwn_password = environ.get("PINHOLE_LWN_PASSWORD", "").strip()
        if lwn_password == "" or lwn_username == "":
            logger.warning(f"PINHOLE_LWN_USERNAME / PINHOLE_LWN_PASSWORD is not properly configured")

        yield FormRequest(
            login_url,
            formdata={
                'Username': lwn_username,
                'Password': lwn_password,
                'target': 'https://lwn.net/',
                'submit': 'Log in'
            },
            callback=self.start_spiding
        )

    def parse_article(self, response: Response, **kwargs) -> Any:
        if response.url not in self.temp_documents:
            return

        document = self.temp_documents[response.url]
        title = response.xpath("//h1/text()").get()
        if title is not None:
            document.set_title(title)

        if 'Weekly Edition' in document.title:
            return

        document.set_content(md(response.text))
        yield document

    def parse(self, response: Response, **kwargs: Any) -> Any:
        blocks = response.text.split('&&')

        for block in blocks[1:]:
            lines = block.splitlines()
            if len(lines) < 4:
                continue

            title = lines[1]
            url = lines[2]
            channel, date_string = str(lines[3]).split(',', 1)
            if channel.strip() not in self.channels:
                continue

            date = dateparser.parse(date_string) or datetime.today()
            self.temp_documents[url] = Document.build(title, date, url, f"LWN {channel}", "")
            yield response.follow(url, self.parse_article)

    def start_spiding(self, response: Response, **kwargs: Any):
        if response.xpath("//title/text()").get().startswith("Log into LWN"):
            logger.warning("invalid username/password given, only explore articles with no need of subscription")

        for url in self.start_urls:
            yield response.follow(url, self.parse)
