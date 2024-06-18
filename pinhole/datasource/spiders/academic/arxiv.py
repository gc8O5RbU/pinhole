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


class ArxivBase(PinholeScrapySpider):

    start_urls = []

    def __init__(self, **kwargs) -> None:
        super(ArxivBase, self).__init__(**kwargs)

    def parse_article(self, response: Response, **kwargs: Any) -> Any:
        title = response.xpath("//meta[@name='citation_title']/@content").get()
        date = dateparser.parse(response.xpath("//meta[@name='citation_date']/@content").get())
        pdf_url = response.xpath("//meta[@name='citation_pdf_url']/@content").get()
        print(title, date, pdf_url)

    def parse(self, response: Response, **kwargs: Any) -> Any:
        for article_addr in response.xpath("//div[@id='dlpage']//a[@title='Abstract']/@href").getall():
            yield response.follow(article_addr, self.parse_article)

        # the first 'small' indicates the top pager in this page
        for pager in response.xpath("//div[@id='dlpage']/small[1]/a/@href").getall():
            yield response.follow(pager, self.parse)


class ArxivSecurity(ArxivBase):
    start_urls = ["https://export.arxiv.org/list/cs.CR/recent"]
