
from pinhole.project import Project
from pinhole.datasource.document import Document, DocumentRef

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic.dataclasses import dataclass, Field
from os import environ
from os.path import isdir, join
from typing import List


app = FastAPI()
project_path = environ['PINHOLE_PROJECT']
project = Project.loadf(project_path) if isdir(project_path) else Project.create(project_path)


@app.get("/")
async def root():
    return {
        "succeeded": True,
        "message": "no method specified"
    }


@app.post("/document/create")
async def create_document(document: Document):
    project.add_document(document)
    return {"succeeded": True}


@app.get("/document/list")
async def list_document():
    return {
        "succeeded": True,
        "documents": project.get_document_refs()
    }


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    content = {
        "succeeded": False,
        "message": f"{type(exc).__name__}: {exc}"
    }

    return JSONResponse(content=content, status_code=status.HTTP_400_BAD_REQUEST)
