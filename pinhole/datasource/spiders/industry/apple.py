from pinhole.datasource.spider import PinholeScrapySpider
from pinhole.datasource.document import Document

from scrapy.responsetypes import Response  # type: ignore
from markdownify import markdownify as md  # type: ignore

from datetime import datetime
from typing import Any

import dateparser
import json


class AppleSecurityBlog(PinholeScrapySpider):

    start_urls = ["https://security.apple.com/blog"]

    def parse_blog(self, response: Response) -> Any:
        title = response.xpath("//h1/text()").get()
        date_str = response.xpath("//aside/div/text()").get()

        try:
            parsed_date = dateparser.parse(date_str) or datetime.today()
        except Exception:
            parsed_date = datetime.today()

        doc = Document.build(
            title, parsed_date, response.url,
            "Apple Inc.", md(response.text)
        )
        yield doc

    def parse(self, response: Response, **kwargs: Any) -> Any:
        content_json = json.loads(response.xpath("//script[@id='__NEXT_DATA__']/text()").get())
        for item in content_json["props"]["pageProps"]["blogs"]:
            slug = item["slug"]
            yield response.follow(f"https://security.apple.com/blog/{slug}", self.parse_blog)
