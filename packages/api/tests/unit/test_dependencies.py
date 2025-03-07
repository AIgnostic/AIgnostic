import pytest
from unittest.mock import patch
from api.router.rabbitmq import create_publisher, get_jobs_publisher


def test_create_publisher():
    with patch("api.router.rabbitmq.Publisher") as mock_publisher:
        publisher_instance = create_publisher()
        mock_publisher.assert_called_once()
        assert publisher_instance == mock_publisher.return_value


def test_get_jobs_publisher():
    with patch("api.router.rabbitmq.Publisher") as mock_publisher:
        create_publisher()
        pub_instance1 = get_jobs_publisher()
        pub_instance2 = get_jobs_publisher()
        assert pub_instance1 is pub_instance2
        assert pub_instance1 == mock_publisher.return_value
