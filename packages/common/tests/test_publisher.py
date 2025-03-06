import pytest
from unittest.mock import patch
from common.rabbitmq.publisher import Publisher


@pytest.fixture
def publisher():
    with patch("common.rabbitmq.publisher.connect_to_rabbitmq"):
        return Publisher(queue="test_queue")


def test_publisher_initialization(publisher):
    assert publisher.queue == "test_queue"
    assert publisher.name == "Publisher"
    assert publisher.is_running is True


def test_publisher_publish(publisher):
    with patch.object(publisher, "channel") as mock_channel:
        publisher._publish("test message")
        mock_channel.basic_publish.assert_called_once_with(
            "", "test_queue", body=b"test message"
        )
        # And check we add _publish to the connection
        publisher.publish("test message")
        publisher.connection.add_callback_threadsafe.assert_called_once()


def test_publisher_stop(publisher):
    with patch.object(publisher.connection, "close") as mock_close:
        publisher.stop()
        assert publisher.is_running is False
        mock_close.assert_called_once()


def test_publisher_tick(publisher):
    with patch.object(publisher.connection, "process_data_events") as mock_process:
        publisher.on_tick()
        mock_process.assert_called()


def test_publisher_run(publisher):
    # Make on_tick immediately throw an exception, expect that to happen and check it was called
    with patch(
        "common.rabbitmq.publisher.Publisher.on_tick", side_effect=Exception
    ) as mock_on_tick:
        with pytest.raises(Exception):
            publisher.run()
        mock_on_tick.assert_called()
