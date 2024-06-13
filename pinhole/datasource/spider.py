from pinhole.datasource.document import Document
from scrapy import Spider  # type: ignore
from scrapy.crawler import CrawlerProcess  # type: ignore
from loguru import logger

from multiprocessing import Process, current_process
from tempfile import mkstemp
from typing import Any, List, Optional

import json


class PinholeSpider:
    name: str = "unknown"
    start_urls: List[str] = []

    def collect(self) -> List[Document]:
        raise NotImplementedError

    def start(self) -> None:
        raise NotImplementedError

    def join(self, timeout: Optional[float] = None) -> None:
        raise NotImplementedError


class PinholeNativeSpider(PinholeSpider):

    def __init__(self) -> None:
        super().__init__()
        self.process: Optional[Process] = None

    def run(self, temp_file: str, log_file: str) -> None:
        raise NotImplementedError

    def start(self) -> None:
        _, self.temp_file = mkstemp(suffix=f"-spider.json")
        _, self.log_file = mkstemp(suffix=f"-spider.log")
        proc = Process(target=self.run, args=(self.temp_file, self.log_file))
        proc.start()
        logger.info(f"native spider started at process {proc.pid}: {self.log_file}")
        self.process = proc

    def join(self, timeout: Optional[float] = None) -> None:
        if self.process is None:
            raise Exception("the spider is not running")

        self.process.join(timeout)

    def collect(self) -> List[Document]:
        return []


class PinholeScrapySpider(PinholeSpider, Spider):

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

        self.process: Optional[Process] = None
        self.temp_file: str = ""
        self.log_file: str = ""

    def __run(self, temp_file: str, log_file: str) -> None:
        settings = {
            'FEEDS': {
                temp_file: {"format": "json"}
            },
            'LOG_FILE': log_file
        }

        cp = CrawlerProcess(settings=settings)
        cp.crawl(type(self))
        cp.start()

    def start(self) -> None:
        _, self.temp_file = mkstemp(suffix=f"-spider.json")
        _, self.log_file = mkstemp(suffix=f"-spider.log")
        proc = Process(target=self.__run, args=(self.temp_file, self.log_file))
        proc.start()
        logger.info(f"spider started at process {proc.pid}: {self.log_file}")
        self.process = proc

    def join(self, timeout: Optional[float] = None) -> None:
        if self.process is None:
            raise Exception("the spider is not running")

        self.process.join(timeout)

    def collect(self) -> List[Document]:
        self.join()

        documents = []
        with open(self.temp_file, "r") as ftemp:
            data = ftemp.read()
            for item in json.loads(data):
                document = Document.from_json(item)
                documents.append(document)

        return documents
