import pytest
from unittest.mock import patch, MagicMock
import pika
from pika.adapters.blocking_connection import BlockingChannel
from common.rabbitmq.connect import connect_to_rabbitmq, init_queues

# Tests created with copilot


@patch("common.rabbitmq.connect.pika.BlockingConnection")
@patch("common.rabbitmq.connect.time.sleep", return_value=None)
def test_connect_to_rabbitmq_success(mock_sleep, mock_blocking_connection):
    mock_blocking_connection.return_value = MagicMock()
    connection = connect_to_rabbitmq(host="localhost", retries=3)
    assert connection is not None
    mock_blocking_connection.assert_called_once()


@patch(
    "common.rabbitmq.connect.pika.BlockingConnection",
    side_effect=pika.exceptions.AMQPConnectionError,
)
@patch("common.rabbitmq.connect.time.sleep", return_value=None)
def test_connect_to_rabbitmq_retry(mock_sleep, mock_blocking_connection):
    with pytest.raises(
        Exception, match="Could not connect to RabbitMQ after 3 attempts."
    ):
        connect_to_rabbitmq(host="localhost", retries=3)
    assert mock_blocking_connection.call_count == 3
    assert mock_sleep.call_count == 3


@patch(
    "common.rabbitmq.connect.pika.BlockingConnection",
    side_effect=pika.exceptions.AMQPConnectionError,
)
@patch("common.rabbitmq.connect.time.sleep", return_value=None)
def test_connect_to_rabbitmq_exhaust_retries(mock_sleep, mock_blocking_connection):
    with pytest.raises(
        Exception, match="Could not connect to RabbitMQ after 10 attempts."
    ):
        connect_to_rabbitmq(host="localhost", retries=10)
    assert mock_blocking_connection.call_count == 10
    assert mock_sleep.call_count == 10


@patch("common.rabbitmq.connect.BlockingChannel")
def test_init_queues(mock_channel):
    channel = MagicMock(spec=BlockingChannel)
    init_queues(channel)
    channel.queue_declare.assert_any_call(queue="job_queue", durable=True)
    channel.queue_declare.assert_any_call(queue="result_queue", durable=True)
