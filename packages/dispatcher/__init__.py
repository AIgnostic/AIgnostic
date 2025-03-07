"""Root entrypoint of the application: starts our FastAPI Server"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dispatcher.dispatcher import api as dispatcher

origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
    "http://host.docker.internal:4200",
    "https://aignostic.docsoc.co.uk",
]


def create_application():
    api = FastAPI(
        title="AIgnostic", description="A FastAPI server for Dispatcher", version="0.1.0"
    )

    # @api.on_event("startup")
    # def connect_rabbit_mq():
    #     from api.router.rabbitmq import fastapi_connect_rabbitmq

    #     return fastapi_connect_rabbitmq()

    api.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api.include_router(dispatcher)
    return api
