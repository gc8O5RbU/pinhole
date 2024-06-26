
from pinhole.datasource.document import Document
from pinhole.datasource.summary import Summary
from pinhole.datasource.publication import Publication
from pinhole.project import Project
from pinhole.user import AuthRequest

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from tempfile import mktemp
from shutil import copy
from typing import Optional
from os import environ, remove
from os.path import isdir

import base64


app = FastAPI()
project_path = environ['PINHOLE_PROJECT']
project = Project.loadf(project_path) if isdir(project_path) else Project.create(project_path)


@app.middleware('http')
async def authentication_middleware(request: Request, call_next):
    authorized = False

    if request.client is not None and request.client.host == '127.0.0.1':
        authorized = True
    else:
        try:
            encoded_email, encoded_pwd = request.headers.get('Authentication', '').split(':')
            email = base64.b64decode(encoded_email).decode('utf-8')
            pwd = base64.b64decode(encoded_pwd).decode('utf-8')
            if pwd == project.admin_password and email == project.admin_email:
                authorized = True
        except Exception as ex:
            pass

    if authorized:
        return await call_next(request)
    else:
        return JSONResponse(
            {
                "succeeded": False,
                "message": "authentication failure"
            },
            status_code=403
        )


@app.get("/")
async def root():
    return {
        "succeeded": True,
        "message": "no method specified"
    }


@app.post("/user/get")
async def get_user_ref(request: AuthRequest):
    return {
        "succeeded": True,
        "user": project.get_user_ref(request.email, request.password)
    }


@app.post("/document/create")
async def create_document(document: Document):
    project.create_document(document)
    return {"succeeded": True}


@app.get("/document/get")
async def get_document(id: int):
    return {
        "succeeded": True,
        "document": project.get_document(id)
    }


@app.get("/document/list")
async def list_document():
    return {
        "succeeded": True,
        "documents": project.get_document_refs()
    }


@app.post("/summary/create")
async def create_summary(summary: Summary):
    project.create_summary(summary)
    return {"succeeded": True}


@app.get("/summary/get")
async def get_summary(document_id: int = -1, publication_id: int = -1):
    summary: Optional[Summary] = None
    if document_id >= 0:
        summary = project.get_summary_of_document(document_id)
    elif publication_id >= 0:
        summary = project.get_summary_of_publication(publication_id)

    return {"succeeded": True, "summary": summary}


@app.post("/publication/create")
async def create_publication(publication: Publication):
    project.create_publication(publication)
    return {"succeeded": True}


@app.get("/publication/list")
async def list_publication():
    return {
        "succeeded": True,
        "publications": project.get_publication_refs()
    }


@app.get("/publication/get")
async def get_publication(id: int):
    return {
        "succeeded": True,
        "publication": project.get_publication(id)
    }


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    content = {
        "succeeded": False,
        "message": f"{type(exc).__name__}: {exc}"
    }

    return JSONResponse(content=content, status_code=status.HTTP_400_BAD_REQUEST)


@app.get("/download/database")
async def download_database():
    tempfile = mktemp()
    copy(project.database_realpath, tempfile)

    with open(tempfile, 'rb') as ftemp:
        content = ftemp.read()

    remove(tempfile)
    return Response(content, headers={
        'Content-Disposition': f'attachment; filename="database.db"'
    })
