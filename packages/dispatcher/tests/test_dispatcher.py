import pytest
from unittest.mock import patch, AsyncMock

from dispatcher.dispatcher import startup, cleanup, connection, redis_client


@pytest.mark.asyncio
@patch("dispatcher.dispatcher.connect_to_rabbitmq")
@patch("dispatcher.dispatcher.connect_to_redis", new_callable=AsyncMock)
async def test_startup_connects_to_services(
    mock_connect_to_redis, mock_connect_to_rabbitmq
):
    await startup()
    mock_connect_to_rabbitmq.assert_called_once()
    mock_connect_to_redis.assert_called_once_with("redis://localhost:6379")


@patch("dispatcher.dispatcher.connection")
def test_cleanup_closes_rabbitmq_connection(mock_connection):
    mock_connection.close = AsyncMock()
    cleanup()
    mock_connection.close.assert_called_once()
