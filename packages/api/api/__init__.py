"""Root entrypoint of the application: starts our FastAPI Server"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.router.api import api as api_router


origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
    "http://host.docker.internal:4200",
]


def create_application():
    api = FastAPI(
        title="AIgnostic", description="A FastAPI server for AIgnostic", version="0.1.0"
    )

    @api.on_event("startup")
    def connect_rabbit_mq():
        from api.router.rabbitmq import fastapi_connect_rabbitmq

        return fastapi_connect_rabbitmq()

    api.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api.include_router(api_router)
    return api
