import os
from celery import Celery
from report_generation.utils import generate_report

# RabbitMQ as the broker
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "pyamqp://guest@rabbitmq//")

app = Celery("tasks", broker=CELERY_BROKER_URL, backend="rpc://")

app.conf.broker_connection_retry_on_startup = True

@app.task
def generate_report_async(aggregates):
    """
    Background task to generate a report asynchronously.
    """
    print("Generating report asynchronously...")
    print("API Key:", os.getenv("GOOGLE_API_KEY"))

    return generate_report(aggregates, os.getenv("GOOGLE_API_KEY"))
