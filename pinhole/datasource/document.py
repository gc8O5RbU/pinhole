from pydantic.dataclasses import dataclass
from pydantic import RootModel, WithJsonSchema
from pydantic import PlainValidator, PlainSerializer, errors

from datetime import datetime
from typing import Annotated, Any


@dataclass(repr=False)
class Document:
    _title: str
    date: datetime
    _url: str
    _publisher: str
    _content: str

    def __repr__(self) -> str:
        return f"<Document {self.title}: {self.date} />"

    @property
    def title(self) -> str:
        return bytes.fromhex(self._title).decode('utf8')

    @property
    def url(self) -> str:
        return bytes.fromhex(self._url).decode('utf8')

    @property
    def publisher(self) -> str:
        return bytes.fromhex(self._publisher).decode('utf8')

    @property
    def content(self) -> str:
        return bytes.fromhex(self._content).decode('utf8')

    @classmethod
    def build(cls, title: str, date: datetime, url: str, publisher: str, content: str) -> 'Document':
        _title = title.encode('utf8').hex()
        _url = url.encode('utf8').hex()
        _publisher = publisher.encode('utf8').hex()
        _content = content.encode('utf8').hex()
        return Document(_title, date, _url, _publisher, _content)

    @classmethod
    def from_json(cls, content: str) -> 'Document':
        return RootModel[Document].model_validate(content).root


@dataclass
class DocumentRef:
    id: int
    _title: str
    date: datetime

    @classmethod
    def build(cls, id: int, title: str, date: datetime) -> 'DocumentRef':
        _title = title.encode('utf8').hex()
        return DocumentRef(id, _title, date)