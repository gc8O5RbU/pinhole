from pinhole.datasource.spiders.all import all_spiders, PinholeSpider
from pinhole.datasource.document import Document, DocumentRef
from pinhole.datasource.summary import Summary
from pinhole.datasource.publication import Publication, PublicationRef
from pinhole.datasource.loaders.arxiv import load_arxiv_content
from pinhole.project import RemoteProject
from pinhole.models.deepseek import DeepSeekChatModel
from pinhole.models.openai import OpenaiChatModel
from pinhole.models.glm import GLMChatModel
from pinhole.models.base import ChatContext, ChatModel
from pinhole.models.profiler import Profiler

from argparse import ArgumentParser, Namespace
from loguru import logger
from typing import List, Union
from typing import Optional

import requests


project = RemoteProject("http://127.0.0.1:8801")


def collector_add_subparser_args(parser: ArgumentParser) -> None:
    parser.add_argument("--spider", type=str,
                        help="specify a list of spiders to run, separated by ','." +
                             "all spiders will be executed by default")
    parser.add_argument("--summarizing", action='store_true',
                        help="run the LLM-based summarization procedure")
    parser.add_argument("--crawling", action="store_true",
                        help="run the crawling spiders")


def crawler(args: Namespace) -> None:
    logger.info("crawler use following spiders")
    spider_instances: List[PinholeSpider] = []

    if args.spider is not None:
        spider_names = {name.strip() for name in args.spider.split(',')}
    else:
        spider_names = {s.__name__ for s in all_spiders}

    for spider in all_spiders:
        if spider.__name__ not in spider_names:
            continue

        spider_names.remove(spider.__name__)
        logger.info(f" - {spider.__name__}")
        spider_instance = spider()
        spider_instance.start()
        spider_instances.append(spider_instance)

    if spider_names:
        logger.warning(f"the following spiders {spider_names} are not found")

    artifacts: List[Union[Document, Publication]] = []
    for spider_instance in spider_instances:
        spider_instance.join()
        artifacts.extend(spider_instance.collect())

    logger.info(f"{len(spider_instances)} spiders finished with {len(artifacts)} artifacts")

    nadded = 0
    existing_urls = {dref.url for dref in project.get_document_refs()}
    existing_urls.update({pref.url for pref in project.get_publication_refs()})

    for artifact in artifacts:
        if isinstance(artifact, Document) and artifact.url not in existing_urls:
            project.create_document(artifact)
            nadded += 1
        elif isinstance(artifact, Publication) and artifact.url not in existing_urls:
            project.create_publication(artifact)
            nadded += 1

    logger.info(f"{nadded} new artifacts are added to the project")


def summarize_documents(args: Namespace) -> None:
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
                summary = Summary.build(dref.id, -1, model.pretty_name(), resp)
                return summary
            except Exception as ex:
                logger.warning(f"model {model.pretty_name()} reports failure: {ex}")

        return None

    drefs_to_summary: List[DocumentRef] = []
    for dref in project.get_document_refs():
        if project.get_summary_of_document(dref.id) is None:
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


def summarize_publications(args: Namespace) -> None:
    profiler = Profiler()
    models: List[ChatModel] = [
        GLMChatModel(model=GLMChatModel.Model.GLM4_AIR),
        OpenaiChatModel(model=OpenaiChatModel.Model.GPT_4O)
    ]

    for model in models:
        model.profiler = profiler

    system_prompt = "你是一个熟悉计算机领域的自身研究者，你的输出以Markdown格式给出。"
    prompt_template = """
    请阅读以下论文内容并用中文给出详细总结，包含论文提出的科研问题，解决方法，核心创新点以及效果总结。
    同时请基于你的经验对于论文方法的可扩展性和应用价值进行评价。

    # 论文标题: {title}

    # 论文内容

    {content}
    """

    def summarize_arxiv(pref: PublicationRef) -> Optional[Summary]:
        content = load_arxiv_content(pref.domain_identifier)
        if content is None:
            logger.error(f"failed to get content of arxiv document {pref.domain_identifier}")
            return None

        for model in models:
            try:
                ctx = ChatContext(model, system_prompt=system_prompt)
                s = ctx.chat(prompt_template.format(title=pref.title, content=content))
                summary = Summary.build(-1, pref.id, model.pretty_name(), s)
                return summary
            except Exception as ex:
                logger.warning(f"model {model.pretty_name()} reports failure: {ex}")

        return None

    prefs_to_summarize: List[PublicationRef] = []
    for pref in project.get_publication_refs():
        if project.get_summary_of_publication(pref.id) is None:
            prefs_to_summarize.append(pref)

    prefs_to_summarize.sort(key=lambda p: p.date, reverse=True)

    N = len(prefs_to_summarize)
    for i, pref in enumerate(prefs_to_summarize):
        publication = project.get_publication(pref.id)
        if publication is None:
            continue

        summary: Optional[Summary] = None
        if publication.publisher == 'arxiv':
            summary = summarize_arxiv(pref)
        else:
            logger.warning(f"unknown publisher {publication.publisher} {publication.title}")

        if summary is not None:
            logger.debug(summary.content)
            project.create_summary(summary)
            logger.info(f"({i}/{N}) summary created for publication {pref.id}: {pref.title}")
        else:
            logger.error(f"({i}/{N}) failed to summarize publication {pref.id}: {pref.title}")

    profiler.print_stats()


def main(args: Namespace) -> None:
    if args.crawling:
        crawler(args)
    if args.summarizing:
        summarize_documents(args)
        summarize_publications(args)
