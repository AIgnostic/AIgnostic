"""Root entrypoint of the application: starts our FastAPI Server"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.router.api import api as api_router
from api.router.rabbitmq import create_publisher


origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
    "http://host.docker.internal:4200",
    "https://aignostic.docsoc.co.uk",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    publisher = create_publisher()
    publisher.start()
    print("RabbitMQ publisher ready")
    yield
    print("Shutting down RabbitMQ publisher")
    publisher.stop()
    publisher.join()


def create_application():

    api = FastAPI(
        title="AIgnostic",
        description="A FastAPI server for AIgnostic",
        version="0.1.0",
        lifespan=lifespan,
    )

    api.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api.include_router(api_router)
    return api
