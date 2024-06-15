from pinhole.datasource.document import Document, DocumentRef
from pydantic.dataclasses import dataclass, Field
from pydantic.root_model import RootModel

from os.path import realpath, join, isdir
from os import makedirs
from typing import Optional, List
from datetime import datetime

import requests
import sqlite3


@dataclass
class RemoteProject:
    base_addr: str = ""

    def create_document(self, document: Document) -> None:
        remote_addr = f"{self.base_addr}/document/create"
        document_json = RootModel[Document](document).model_dump_json()

        req = requests.post(remote_addr, data=document_json,)
        if req.status_code == 422:
            raise Exception(f"failed to create document: {req.text}")
        elif req.status_code != 200:
            raise Exception(f"document creation failed")

        response = req.json()
        if response['succeeded'] is False:
            raise Exception(f"documen creation failed: {response['message']}")


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

    ###########################################################################
    # Assistant functions for managing documents
    ###########################################################################

    @property
    def __dbconn(self) -> sqlite3.Connection:
        if hasattr(self, "__dbconn__"):
            return getattr(self, "__dbconn__")

        dbconn = sqlite3.connect(join(self.project_path, self.database_path))
        setattr(self, "__dbconn__", dbconn)
        return dbconn

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

    def add_document(self, document: Document) -> None:
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

    def get_document(self, id: int) -> Optional[Document]:
        pass

    def get_document_by_url(self, url: str) -> Optional[Document]:
        pass

    def get_document_refs(self) -> List[DocumentRef]:
        self.__create_document_table()
        cur = self.__dbconn.cursor()
        sql = "SELECT id, title, date FROM documents"
        cur.execute(sql)

        result = []
        for (id, title, date) in cur.fetchall():
            result.append(DocumentRef.build(
                id, title, datetime.fromtimestamp(date)
            ))

        return result
