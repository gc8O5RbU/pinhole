from pinhole.datasource.spider import PinholeScrapySpider
from pinhole.datasource.publication import Publication

from scrapy.responsetypes import Response  # type: ignore
from datetime import datetime
from typing import Any

import dateparser


class ArxivBase(PinholeScrapySpider):

    start_urls = []

    def __init__(self, **kwargs) -> None:
        super(ArxivBase, self).__init__(**kwargs)

    def parse_article(self, response: Response, **kwargs: Any) -> Any:
        title = response.xpath("//meta[@name='citation_title']/@content").get()
        date = dateparser.parse(response.xpath("//meta[@name='citation_date']/@content").get()) or datetime.today()
        arxiv_id = response.xpath("//meta[@name='citation_arxiv_id']/@content").get()
        authors = response.xpath("//meta[@name='citation_author']/@content").getall()
        abstract = response.xpath("//blockquote/text()[2]").get()
        publication = Publication.build(
            title, authors, date, "", response.url, "arxiv", arxiv_id, "preprint", abstract
        )
        yield publication

    def parse(self, response: Response, **kwargs: Any) -> Any:
        for article_addr in response.xpath("//div[@id='dlpage']//a[@title='Abstract']/@href").getall():
            yield response.follow(article_addr, self.parse_article)

        # the first 'small' indicates the top pager in this page
        for pager in response.xpath("//div[@id='dlpage']/small[1]/a/@href").getall():
            yield response.follow(pager, self.parse)


class ArxivSecurity(ArxivBase):
    start_urls = ["https://export.arxiv.org/list/cs.CR/new"]


class ArxivComputationLanguage(ArxivBase):
    start_urls = ["https://export.arxiv.org/list/cs.CL/new"]
