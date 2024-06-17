from pinhole.datasource.spider import PinholeSpider
from pinhole.datasource.spiders.industry.apple import AppleSecurityBlog
from pinhole.datasource.spiders.industry.microsoft import MicrosoftSecurityBlog
from pinhole.datasource.document import Document, Summary
from pinhole.project import RemoteProject
from pinhole.models.glm import GLMChatModel
from pinhole.models.base import ChatContext
from pinhole.models.profiler import Profiler

from loguru import logger
from typing import List
from typing import Type as SubType


spiders: List[SubType[PinholeSpider]] = [
    AppleSecurityBlog,
    # MicrosoftSecurityBlog
]

project = RemoteProject("http://127.0.0.1:8000")


def crawler() -> None:
    logger.info("crawler use following spiders")
    spider_instances: List[PinholeSpider] = []
    for spider in spiders:
        logger.info(f" - {spider.__name__}")
        spider_instance = spider()
        spider_instance.start()
        spider_instances.append(spider_instance)

    documents: List[Document] = []
    for spider_instance in spider_instances:
        spider_instance.join()
        documents.extend(spider_instance.collect())

    logger.info(f"{len(spider_instances)} spiders finished with {len(documents)} documents")

    nadded = 0
    existing_urls = {dref.url for dref in project.get_document_refs()}
    for document in documents:
        if document.url not in existing_urls:
            project.create_document(document)
            nadded += 1

    logger.info(f"{nadded} new documents are added to the project")


def summarizer() -> None:
    profiler = Profiler()
    model = GLMChatModel()
    model.profiler = profiler
    ctx = ChatContext(model)
    ctx.system_prompt = "你是一个熟悉计算机领域的自身研究者，你的输出以Markdown格式给出。"
    prompt = """
    请阅读以下文章内容并用中文给出简单总结，同时列出其中你认为最有价值的核心内容。

    # {title}

    {content}
    """

    for dref in project.get_document_refs():
        if project.get_summary(dref.id) is None:
            document = project.get_document(dref.id)
            assert document is not None
            summary_content = ctx.fork().chat(prompt.format(title=document.title, content=document.content))
            summary = Summary.build(dref.id, model.pretty_name(), summary_content)
            project.create_summary(summary)


def main() -> None:
    logger.info("start information collecting")
    crawler()
    summarizer()
