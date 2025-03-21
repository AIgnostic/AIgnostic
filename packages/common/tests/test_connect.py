import redis
import pytest
from unittest.mock import patch, MagicMock
import pika
import pika.exceptions
from pika.adapters.blocking_connection import BlockingChannel
from common.rabbitmq.connect import connect_to_rabbitmq, init_queues, publish_to_queue
from common.redis.connect import connect_to_redis

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


@patch("common.redis.connect.redis.Redis.from_url")
@patch("common.redis.connect.sleep", return_value=None)
def test_connect_to_redis_success(mock_sleep, mock_redis_from_url):
    mock_redis_client = MagicMock()
    mock_redis_client.ping = MagicMock(return_value=True)
    mock_redis_from_url.return_value = mock_redis_client

    redis_client = connect_to_redis(url="redis://localhost", retries=3)
    assert redis_client is not None
    mock_redis_from_url.assert_called_once_with("redis://localhost")
    mock_redis_client.ping.assert_called_once()


@patch("common.redis.connect.redis.Redis.from_url", side_effect=redis.ConnectionError)
@patch("common.redis.connect.sleep", return_value=None)
@pytest.mark.asyncio
async def test_connect_to_redis_retry(mock_sleep, mock_redis_from_url):
    with pytest.raises(Exception):
        connect_to_redis(url="redis://localhost", retries=3)
    assert mock_redis_from_url.call_count == 3
    assert mock_sleep.call_count == 3


@patch("common.redis.connect.redis.Redis.from_url", side_effect=redis.ConnectionError)
@patch("common.redis.connect.sleep", return_value=None)
def test_connect_to_redis_exhaust_retries(mock_sleep, mock_redis_from_url):
    with pytest.raises(Exception):
        connect_to_redis(url="redis://localhost", retries=10)
    assert mock_redis_from_url.call_count == 10
    assert mock_sleep.call_count == 10


@patch("common.rabbitmq.connect.connect_to_rabbitmq")
def test_publish_to_channel_success(mock_connect_to_rabbitmq):
    """Test successful message publishing"""
    mock_channel = MagicMock(spec=BlockingChannel)

    with patch.object(mock_channel, "basic_publish") as mock_basic_publish:
        publish_to_queue(mock_channel, "test_queue", "test_message")

    mock_basic_publish.assert_called_once_with(
        exchange="", routing_key="test_queue", body="test_message"
    )


@patch("common.rabbitmq.connect.connect_to_rabbitmq")
def test_publish_to_channel_reconnect(mock_connect_to_rabbitmq):
    """Test publishing when the first attempt fails and requires reconnection"""
    mock_channel = MagicMock(spec=BlockingChannel)

    mock_new_channel = MagicMock(spec=BlockingChannel)
    mock_connection = MagicMock()
    mock_connection.channel.return_value = mock_new_channel
    mock_connect_to_rabbitmq.return_value = mock_connection

    with patch.object(mock_channel, "basic_publish", side_effect=pika.exceptions.AMQPConnectionError) \
         as mock_basic_publish, \
         patch.object(mock_new_channel, "basic_publish") as mock_new_basic_publish:
        publish_to_queue(mock_channel, "test_queue", "test_message")

        # First attempt failed, so it should retry
        mock_basic_publish.assert_called_once_with(
            exchange="", routing_key="test_queue", body="test_message"
        )
        mock_connect_to_rabbitmq.assert_called_once()
        mock_new_basic_publish.assert_called_once_with(
            exchange="", routing_key="test_queue", body="test_message"
        )
