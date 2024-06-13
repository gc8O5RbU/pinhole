from pinhole.datasource.spider import PinholeScrapySpider
from pinhole.datasource.document import Document, DocumentContent

from scrapy.responsetypes import Response  # type: ignore
from markdownify import markdownify as md  # type: ignore

from datetime import datetime
from typing import Any, Set

import dateparser
import json


class MicrosoftSecurityBlog(PinholeScrapySpider):

    start_urls = ["https://www.microsoft.com/en-us/security/blog"]

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

        self.visited_urls: Set[str] = set()

    def parse_json_list(self, response: Response, **kwargs: Any) -> Any:
        print(response.text)

    def parse(self, response: Response, **kwargs: Any) -> Any:
        if response.url in self.visited_urls:
            return
        elif not response.url.startswith("https://www.microsoft.com/en-us/security/blog"):
            return

        self.visited_urls.add(response.url)
        article_links = response.xpath("//article//a/@href").getall()
        for link in article_links:
            yield response.follow(link, self.parse)

        title = response.xpath("//header//h1/text()").get()
        if title is not None:
            date = dateparser.parse(response.xpath("//main//time/text()").get()) or datetime.today()
            doc = Document(title, date, response.url, 'Microsoft', DocumentContent(md(response.text)))
            yield doc
