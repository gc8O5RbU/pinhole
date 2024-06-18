from pinhole.datasource.spider import PinholeSpider
from pinhole.datasource.spiders.industry.apple import AppleSecurityBlog
from pinhole.datasource.spiders.industry.microsoft import MicrosoftSecurityBlog
from pinhole.datasource.spiders.community.lwn import LwnHeadline
from pinhole.datasource.document import Document, DocumentRef, Summary
from pinhole.project import RemoteProject
from pinhole.models.deepseek import DeepSeekChatModel
from pinhole.models.openai import OpenaiChatModel
from pinhole.models.base import ChatContext, ChatModel
from pinhole.models.profiler import Profiler

from argparse import ArgumentParser, Namespace
from loguru import logger
from typing import List
from typing import Optional, Type as SubType


spiders: List[SubType[PinholeSpider]] = [
    # AppleSecurityBlog,
    # MicrosoftSecurityBlog,
    LwnHeadline
]

project = RemoteProject("http://127.0.0.1:8000")


def collector_add_subparser_args(parser: ArgumentParser) -> None:
    parser.add_argument("--no-summarize", action='store_true',
                        help="do not run the LLM-based summarization procedure")


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
    models: List[ChatModel] = [DeepSeekChatModel(), OpenaiChatModel()]
    for model in models:
        model.profiler = profiler

    system_prompt = "你是一个熟悉计算机领域的自身研究者，你的输出以Markdown格式给出。"
    prompt_template = """
    请阅读以下文章内容并用中文给出简单总结，同时列出其中你认为最有价值的核心内容。

    # {title}

    {content}
    """

    def generate_summary(document: Document) -> Optional[Summary]:
        for model in models:
            try:
                ctx = ChatContext(model, system_prompt=system_prompt)
                resp = ctx.chat(prompt_template.format(title=document.title, content=document.content))
                summary = Summary.build(dref.id, model.pretty_name(), resp)
                return summary
            except Exception as ex:
                logger.warning(f"model {model.pretty_name()} reports failure: {ex}")

        return None

    drefs_to_summary: List[DocumentRef] = []
    for dref in project.get_document_refs():
        if project.get_summary(dref.id) is None:
            drefs_to_summary.append(dref)

    drefs_to_summary.sort(key=lambda dref: dref.date, reverse=True)
    N = len(drefs_to_summary)
    for i, dref in enumerate(drefs_to_summary):
        document = project.get_document(dref.id)
        assert document is not None
        summary = generate_summary(document)
        if summary is not None:
            project.create_summary(summary)
            logger.info(f"({i}/{N}) summary created for document {dref.id}: {dref.title}")
        else:
            logger.error(f"({i}/{N}) failed to summarize document {dref.id}: {dref.title}")

    profiler.print_stats()


def main(args: Namespace) -> None:
    logger.info("start information collecting")
    crawler()
    if not args.no_summarize:
        summarizer()
