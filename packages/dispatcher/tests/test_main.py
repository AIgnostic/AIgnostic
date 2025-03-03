import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from dispatcher.__main__ import startup, cleanup


@patch("dispatcher.__main__.connect_to_rabbitmq")
@patch("dispatcher.__main__.connect_to_redis", new_callable=AsyncMock)
def test_startup_connects_to_services(mock_connect_to_redis, mock_connect_to_rabbitmq):
    startup()
    mock_connect_to_rabbitmq.assert_called_once()
    mock_connect_to_redis.assert_called_once_with("redis://localhost:6379")


def test_cleanup_closes_rabbitmq_connection():
    mock_connection = MagicMock()
    cleanup(mock_connection)
    mock_connection.close.assert_called_once()
