from pinhole.datasource.utils import hexstr2str, str2hexstr

from pydantic.dataclasses import dataclass, Field
from pydantic.root_model import RootModel
from typing import List, Literal
from datetime import datetime


PublicationType = Literal['journal', 'conference', 'preprint', 'article']


@dataclass
class Publication:
    _title: str
    _authors: str
    date: datetime
    _booktitle: str
    _url: str
    _publisher: str
    _domain_identifier: str
    type: PublicationType
    _abstract: str = ""

    @classmethod
    def build(cls, title: str,
              authors: List[str],
              date: datetime,
              booktitle: str,
              url: str,
              publisher: str,
              domain_identifier: str = "",
              type: PublicationType = 'article',
              abstract: str = "") -> 'Publication':

        pub = Publication("", "", date, "", "", "", "", type)
        pub.set_title(title)
        pub.set_authors(authors)
        pub.set_booktitle(booktitle)
        pub.set_url(url)
        pub.set_publisher(publisher)
        pub.set_domain_identifier(domain_identifier)
        pub.set_abstract(abstract)

        return pub

    @property
    def title(self) -> str:
        return hexstr2str(self._title)

    def set_title(self, title: str) -> None:
        self._title = str2hexstr(title)

    @property
    def authors(self) -> List[str]:
        return [hexstr2str(a) for a in self._authors.split("|")]

    def set_authors(self, authors: List[str]):
        self._authors = "|".join(str2hexstr(a) for a in authors)

    @property
    def booktitle(self) -> str:
        return hexstr2str(self._booktitle)

    def set_booktitle(self, booktitle: str) -> None:
        self._booktitle = str2hexstr(booktitle)

    @property
    def url(self) -> str:
        return hexstr2str(self._url)

    def set_url(self, url: str) -> None:
        self._url = str2hexstr(url)

    @property
    def domain_identifier(self) -> str:
        return hexstr2str(self._domain_identifier)

    def set_domain_identifier(self, domain_identifier: str) -> None:
        self._domain_identifier = str2hexstr(domain_identifier)

    @property
    def publisher(self) -> str:
        return hexstr2str(self._publisher)

    def set_publisher(self, publisher: str) -> None:
        self._publisher = str2hexstr(publisher)

    @property
    def abstract(self) -> str:
        return hexstr2str(self._abstract)

    def set_abstract(self, abstract: str) -> None:
        self._abstract = str2hexstr(abstract)

    @classmethod
    def from_json(cls, data: str) -> 'Publication':
        return RootModel[Publication].model_validate(data).root


@dataclass
class PublicationRef:
    id: int
    _title: str
    date: datetime
    _booktitle: str
    _url: str
    _domain_identifier: str
    type: PublicationType

    @classmethod
    def build(cls, id: int,
              title: str,
              date: datetime,
              booktitle: str,
              url: str,
              domain_identifier: str = "",
              type: PublicationType = 'article') -> 'PublicationRef':

        pub = PublicationRef(id, "", date, "", "", "", type)
        pub.set_title(title)
        pub.set_booktitle(booktitle)
        pub.set_url(url)
        pub.set_domain_identifier(domain_identifier)

        return pub

    @property
    def title(self) -> str:
        return hexstr2str(self._title)

    def set_title(self, title: str) -> None:
        self._title = str2hexstr(title)

    @property
    def booktitle(self) -> str:
        return hexstr2str(self._booktitle)

    def set_booktitle(self, booktitle: str) -> None:
        self._booktitle = str2hexstr(booktitle)

    @property
    def url(self) -> str:
        return hexstr2str(self._url)

    def set_url(self, url: str) -> None:
        self._url = str2hexstr(url)

    @property
    def domain_identifier(self) -> str:
        return hexstr2str(self._domain_identifier)

    def set_domain_identifier(self, domain_identifier: str) -> None:
        self._domain_identifier = str2hexstr(domain_identifier)

    @classmethod
    def from_json(cls, data: str) -> 'PublicationRef':
        return RootModel[PublicationRef].model_validate(data).root
