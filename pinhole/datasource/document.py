from pydantic.dataclasses import dataclass, Field
from pydantic.types import date
from pydantic import RootModel


@dataclass
class DocumentContent:
    text: str


@dataclass
class Document:
    title: str
    date: date
    url: str
    publisher: str
    content: DocumentContent

    @classmethod
    def from_json(cls, content: str) -> 'Document':
        return RootModel[Document].model_validate(content).root
