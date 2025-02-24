from unittest.mock import patch, MagicMock
from api.router.api import dispatch_job
from common.rabbitmq.constants import JOB_QUEUE


@patch("pika.BlockingConnection")
def test_dispatch_job(mock_connection):
    # Mock the channel object returned by the connection
    mock_channel = MagicMock()
    mock_connection.return_value.channel.return_value = mock_channel

    # Sample data for testing
    batch_size = 10
    metrics = ["accuracy", "precision"]
    data_url = "https://example.com/data"
    model_url = "https://example.com/model"
    data_api_key = "data-key"
    model_api_key = "model-key"

    # Dispatch job
    dispatch_job(
        batch_size=batch_size,
        total_sample_size=100,
        metrics=metrics,
        model_type="binary classification",
        data_url=data_url,
        model_url=model_url,
        data_api_key=data_api_key,
        model_api_key=model_api_key,
        channel=mock_channel,
    )

    # Assert that `basic_publish` was called once
    mock_channel.basic_publish.assert_called_once()

    # Extract the call arguments
    call_args = mock_channel.basic_publish.call_args[1]
    assert call_args["exchange"] == ""
    assert call_args["routing_key"] == JOB_QUEUE
    assert call_args["body"] is not None
