from pinhole.datasource.utils import str2hexstr, hexstr2str

from pydantic.dataclasses import dataclass
from pydantic import RootModel

from datetime import datetime


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

    def set_title(self, title: str) -> None:
        self._title = title.encode('utf8').hex()

    @property
    def url(self) -> str:
        return bytes.fromhex(self._url).decode('utf8')

    @property
    def publisher(self) -> str:
        return bytes.fromhex(self._publisher).decode('utf8')

    @property
    def content(self) -> str:
        return bytes.fromhex(self._content).decode('utf8')

    def set_content(self, content: str) -> None:
        self._content = content.encode('utf8').hex()

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
    _url: str
    _publisher: str

    @property
    def title(self) -> str:
        return bytes.fromhex(self._title).decode('utf8')

    @property
    def url(self) -> str:
        return bytes.fromhex(self._url).decode('utf8')

    @property
    def publisher(self) -> str:
        return bytes.fromhex(self._publisher).decode('utf8')

    @classmethod
    def build(cls, id: int, title: str, date: datetime, url: str, publisher: str) -> 'DocumentRef':
        _title = title.encode('utf8').hex()
        _url = url.encode('utf8').hex()
        _publisher = publisher.encode('utf8').hex()
        return DocumentRef(id, _title, date, _url, _publisher)

    @classmethod
    def from_json(cls, content: str) -> 'DocumentRef':
        return RootModel[DocumentRef].model_validate(content).root


@dataclass(repr=False)
class Summary:
    document_id: int
    _model: str
    _content: str

    def __repr__(self) -> str:
        return f"<Summary of document {self.document_id} />"

    @property
    def model(self) -> str:
        return hexstr2str(self._model)

    @property
    def content(self) -> str:
        return hexstr2str(self._content)

    @classmethod
    def build(cls, document_id: int, model: str, publisher: str) -> 'Summary':
        _model = str2hexstr(model)
        _publisher = str2hexstr(publisher)
        return Summary(document_id, _model, _publisher)

    @classmethod
    def from_json(cls, content: str) -> 'Summary':
        return RootModel[Summary].model_validate(content).root
