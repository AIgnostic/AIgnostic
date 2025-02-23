import pytest
from unittest.mock import MagicMock, patch
from aggregator.aggregator import ResultsConsumer, RESULT_QUEUE

@pytest.fixture
def consumer():
    return ResultsConsumer(host="test_host")

def test_init(consumer):
    assert consumer._host == "test_host"
    assert consumer._connection is None
    assert consumer._channel is None

@patch('common.rabbitmq.connect.connect_to_rabbitmq')
@patch('common.rabbitmq.connect.init_queues')
def test_connect(mock_init_queues, mock_connect_to_rabbitmq, consumer):
    mock_connection = MagicMock()
    mock_channel = MagicMock()
    mock_connect_to_rabbitmq.return_value = mock_connection
    mock_connection.channel.return_value = mock_channel

    consumer.connect()

    mock_connect_to_rabbitmq.assert_called_once_with(host="test_host")
    mock_connection.channel.assert_called_once()
    mock_init_queues.assert_called_once_with(mock_channel)
    assert consumer._connection == mock_connection
    assert consumer._channel == mock_channel

    # Add these print statements for debugging
    print(f"mock_connect_to_rabbitmq called: {mock_connect_to_rabbitmq.called}")
    print(f"mock_init_queues called: {mock_init_queues.called}")

@patch('common.rabbitmq.connect.init_queues')
@patch('common.rabbitmq.connect.connect_to_rabbitmq')
def test_run(mock_init_queues, mock_connect_to_rabbitmq, consumer):
    mock_connection = MagicMock()
    mock_channel = MagicMock()
    mock_connect_to_rabbitmq.return_value = mock_connection
    mock_connection.channel.return_value = mock_channel

    mock_callback = MagicMock()

    consumer.run(on_message_callback=mock_callback)

    mock_channel.basic_consume.assert_called_once_with(
        queue=RESULT_QUEUE,
        on_message_callback=mock_callback,
        auto_ack=True
    )
    mock_channel.start_consuming.assert_called_once()

@patch('common.rabbitmq.connect.connect_to_rabbitmq')
@patch('common.rabbitmq.connect.init_queues')
def test_stop(mock_init_queues, mock_connect_to_rabbitmq, consumer):
    mock_connection = MagicMock()
    mock_channel = MagicMock()
    consumer._connection = mock_connection
    consumer._channel = mock_channel

    consumer.stop()

    mock_channel.close.assert_called_once()
    mock_connection.close.assert_called_once()
