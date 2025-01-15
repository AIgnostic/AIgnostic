from pydantic import BaseModel
from fastapi import APIRouter

api = APIRouter()


@api.get("/")
def hello():
    return {"message": "Hello World!"}


@api.get("/repeat/{text}")  # /repeat/hello, /repeat/a,
def repeat(text: str):
    return {"message": text}


class Request(BaseModel):  # class Request extends BaseModel
    text: str


@api.post("/echo")
def echo(request: Request):
    return {"message": request.text}
