from unittest.mock import patch

import pytest


@pytest.mark.asyncio
async def test_lifespan_publisher():
    with patch("api.create_publisher") as mock_create_pub:
        from api import lifespan

        mock_publisher = mock_create_pub.return_value
        async with lifespan(None) as _:
            pass
        mock_create_pub.assert_called_once()
        mock_publisher.start.assert_called_once()
        mock_publisher.stop.assert_called_once()
        mock_publisher.join.assert_called_once()
