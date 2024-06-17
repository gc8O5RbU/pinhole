from pinhole.datasource.document import Document, DocumentRef, Summary
from pydantic.dataclasses import dataclass, Field
from pydantic.root_model import RootModel

from os.path import realpath, join, isdir
from os import makedirs
from typing import Optional, List, Any, Dict
from datetime import datetime

import requests
import sqlite3


class AbstractProject:
    """ The abstract base class for `RemoteProject` and `Project`. The design aims
    to guarantee that the API interface of the two types of projects remain exactly
    the same. """

    def create_document(self, document: Document) -> None:
        raise NotImplementedError

    def get_document(self, document_id: int) -> Optional[Document]:
        raise NotImplementedError

    def create_summary(self, summary: Summary) -> None:
        raise NotImplementedError

    def get_summary(self, document_id: int) -> Optional[Summary]:
        raise NotImplementedError


@dataclass
class RemoteProject:
    base_addr: str = ""

    def __get(self, url: str) -> Dict[str, Any]:
        req = requests.get(url)
        if req.status_code != 200:
            raise Exception(f"request failed with status code {req.status_code}: {req.text} in {url}")

        resp = req.json()
        if resp is None:
            raise Exception(f"request failed because response is not a valid json: {req.text}")

        if resp['succeeded'] is False:
            raise Exception(f"request failed: {resp['message']} in {url}")

        return resp

    def __post(self, url: str, data: Any = None) -> Dict[str, Any]:
        req = requests.post(url, data=data)
        if req.status_code != 200:
            raise Exception(f"request failed with status code {req.status_code}: {req.text} in {url}")

        resp = req.json()
        if resp is None:
            raise Exception(f"request failed because response is not a valid json: {req.text}")

        if resp['succeeded'] is False:
            raise Exception(f"request failed: {resp['message']} in {url}")

        return resp

    def create_document(self, document: Document) -> None:
        remote_addr = f"{self.base_addr}/document/create"
        document_json = RootModel[Document](document).model_dump_json()

        self.__post(remote_addr, data=document_json)

    def get_document(self, document_id: int) -> Optional[Document]:
        remote_addr = f"{self.base_addr}/document/get?id={document_id}"
        resp = self.__get(remote_addr)
        if resp["document"] is None:
            return None
        else:
            return Document.from_json(resp["document"])

    def get_document_refs(self) -> List[DocumentRef]:
        remote_addr = f"{self.base_addr}/document/list"
        resp = self.__get(remote_addr)

        drefs = []
        for document in resp['documents']:
            dref = DocumentRef.from_json(document)
            drefs.append(dref)

        return drefs

    def create_summary(self, summary: Summary) -> None:
        remote_addr = f"{self.base_addr}/summary/create"
        summary_json = RootModel[Summary](summary).model_dump_json()
        self.__post(remote_addr, data=summary_json)

    def get_summary(self, document_id: int) -> Optional[Summary]:
        remote_addr = f"{self.base_addr}/summary/get?document_id={document_id}"
        resp = self.__get(remote_addr)

        if resp["summary"] is None:
            return None
        else:
            return Summary.from_json(resp["summary"])


@dataclass
class Project:
    database_path: str
    vector_store_path: str

    def set_project_path(self, path: str) -> None:
        setattr(self, "__path__", path)

    @property
    def project_path(self) -> str:
        return getattr(self, "__path__", "")

    @classmethod
    def create(cls, path: str) -> 'Project':
        project_path = realpath(path)
        if not isdir(project_path):
            makedirs(project_path, exist_ok=True)

        project = Project("db.sqlite", "")
        project.set_project_path(project_path)
        project.save()
        return project

    @classmethod
    def loadf(cls, path: str) -> 'Project':
        project_path = realpath(path)
        with open(join(project_path, "project.json"), "r") as f:
            project = RootModel[Project].model_validate_json(f.read()).root
            project.set_project_path(project_path)
            return project

    def save(self) -> None:
        with open(join(self.project_path, "project.json"), "w+") as f:
            f.write(RootModel[Project](self).model_dump_json())

    @property
    def __dbconn(self) -> sqlite3.Connection:
        if hasattr(self, "__dbconn__"):
            return getattr(self, "__dbconn__")

        dbconn = sqlite3.connect(join(self.project_path, self.database_path))
        setattr(self, "__dbconn__", dbconn)
        return dbconn

    ###########################################################################
    # Assistant functions for managing documents
    ###########################################################################

    def __create_document_table(self) -> None:
        cur = self.__dbconn.cursor()
        sql = """
        CREATE TABLE IF NOT EXISTS documents (
            id integer PRIMARY KEY,
            title text NOT NULL,
            date integer NOT NULL,
            url text NOT NULL UNIQUE,
            publisher text,
            content text
        )
        """
        cur.execute(sql)

    def create_document(self, document: Document) -> None:
        self.__create_document_table()
        cur = self.__dbconn.cursor()
        sql = f"""
        INSERT INTO documents
            (title, date, url, publisher, content) VALUES
            (?, ?, ?, ?, ?)
        """
        cur.execute(
            sql,
            (document.title, document.date.timestamp(), document.url,
             document.publisher, document.content)
        )
        self.__dbconn.commit()

    def get_document(self, document_id: int) -> Optional[Document]:
        self.__create_document_table()
        cur = self.__dbconn.cursor()
        sql = "SELECT title, date, url, publisher, content FROM documents WHERE id = ?"
        cur.execute(sql, (document_id,))

        rows = cur.fetchall()
        if len(rows) == 0:
            return None

        assert len(rows) == 1
        (title, date, url, publisher, content) = rows[0]
        return Document.build(title, datetime.fromtimestamp(date), url, publisher, content)

    def get_document_by_url(self, url: str) -> Optional[Document]:
        pass

    def get_document_refs(self) -> List[DocumentRef]:
        self.__create_document_table()
        cur = self.__dbconn.cursor()
        sql = "SELECT id, title, date, url, publisher FROM documents"
        cur.execute(sql)

        result = []
        for (id, title, date, url, publisher) in cur.fetchall():
            result.append(DocumentRef.build(
                id, title, datetime.fromtimestamp(date),
                url, publisher
            ))

        return result

    ###########################################################################
    # Assistant functions for managing summaries
    ###########################################################################

    def __create_summaries_table(self) -> None:
        cur = self.__dbconn.cursor()
        sql = """
        CREATE TABLE IF NOT EXISTS summaries (
            id integer PRIMARY KEY,
            document_id integer UNIQUE,
            model text,
            content text
        )
        """
        cur.execute(sql)

    def create_summary(self, summary: Summary) -> None:
        self.__create_document_table()
        cur = self.__dbconn.cursor()
        sql = f"""
        INSERT INTO summaries
            (document_id, model, content) VALUES
            (?, ?, ?)
        """
        cur.execute(
            sql,
            (summary.document_id, summary.model, summary.content)
        )
        self.__dbconn.commit()

    def get_summary(self, document_id: int) -> Optional[Summary]:
        self.__create_summaries_table()
        cur = self.__dbconn.cursor()
        sql = "SELECT id, document_id, model, content FROM summaries WHERE document_id == ?"
        cur.execute(sql, (document_id,))
        rows = cur.fetchall()

        if len(rows) == 0:
            return None

        assert len(rows) == 1
        (id, document_id, model, summary) = rows[0]
        return Summary.build(document_id, model, summary)
