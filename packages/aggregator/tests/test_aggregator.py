import time
import pytest
from unittest.mock import MagicMock, mock_open, patch
from aggregator.aggregator import (
    RESULT_QUEUE,
    MetricsAggregator,
    ResultsConsumer,
    aggregator_final_report_log,
    aggregator_generate_report,
    generate_and_send_report,
    get_api_key,
    on_result_fetched,
    aggregator_intermediate_metrics_log,
    aggregator_metrics_completion_log,
    connected_clients,
    message_queue,
    websocket_handler,
    send_to_clients,
    user_aggregators,
    manager,
)
import json
from common.models import AggregatorJob, JobType, WorkerError


@pytest.fixture(scope="module")
def consumer():
    return ResultsConsumer(host="test_host")


metrics_aggregator = MetricsAggregator()


@pytest.fixture(autouse=True)
def reset_state():
    metrics_aggregator.metrics = {}
    metrics_aggregator.samples_processed = 0
    metrics_aggregator.total_sample_size = 0
    user_aggregators.clear()
    connected_clients.clear()
    while not message_queue.empty():
        message_queue.get()


def test_init(consumer):
    assert consumer._host == "test_host"
    assert consumer._connection is None
    assert consumer._channel is None


@patch("aggregator.aggregator.connect_to_rabbitmq")
@patch("aggregator.aggregator.init_queues")
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


@patch("aggregator.aggregator.init_queues")
@patch("aggregator.aggregator.connect_to_rabbitmq")
def test_run(mock_init_queues, mock_connect_to_rabbitmq, consumer):
    mock_connection = MagicMock()
    mock_channel = MagicMock()
    mock_connect_to_rabbitmq.return_value = mock_connection
    mock_connection.channel.return_value = mock_channel

    consumer.connect = MagicMock()
    consumer._connection = mock_connection
    consumer._channel = mock_channel

    mock_callback = MagicMock()
    mock_channel.start_consuming = MagicMock()

    consumer.run(on_message_callback=mock_callback)

    mock_channel.basic_consume.assert_called_once_with(
        queue=RESULT_QUEUE, on_message_callback=mock_callback, auto_ack=True
    )
    mock_channel.start_consuming.assert_called_once()


@patch("aggregator.aggregator.connect_to_rabbitmq")
@patch("aggregator.aggregator.init_queues")
def test_stop(mock_init_queues, mock_connect_to_rabbitmq, consumer):
    mock_connection = MagicMock()
    mock_channel = MagicMock()
    consumer._connection = mock_connection
    consumer._channel = mock_channel

    consumer.stop()

    mock_channel.close.assert_called_once()
    mock_connection.close.assert_called_once()


@patch("aggregator.aggregator.connect_to_rabbitmq")
@patch("aggregator.aggregator.init_queues")
@patch.object(ResultsConsumer, "stop")  # Mock stop to prevent real shutdown
def test_run_keyboard_interrupt(
    mock_stop, mock_init_queues, mock_connect_to_rabbitmq, consumer
):
    mock_connection = MagicMock()
    mock_channel = MagicMock()

    mock_connect_to_rabbitmq.return_value = mock_connection
    mock_connection.channel.return_value = mock_channel

    consumer.connect = MagicMock()  # Prevent real connection logic
    consumer._connection = mock_connection
    consumer._channel = mock_channel

    mock_callback = MagicMock()

    # Simulate `start_consuming` raising a KeyboardInterrupt
    mock_channel.start_consuming.side_effect = KeyboardInterrupt

    consumer.run(on_message_callback=mock_callback)

    # Ensure that stop() is called when KeyboardInterrupt occurs
    mock_stop.assert_called_once()


def test_on_result_fetched_for_error():
    body = AggregatorJob(
        job_type=JobType.ERROR,
        content=WorkerError(
            error_message="An error occurred",
            error_code=500
        )
    )
    bodyJson = body.model_dump_json()
    with patch("aggregator.aggregator.process_error_result", new_callable=MagicMock) as mock_process_error_result:
        on_result_fetched(None, None, None, bodyJson)
        mock_process_error_result.assert_called_once_with(error_data=body.content)


@patch('aggregator.aggregator.manager.send_to_user')
@patch('aggregator.aggregator.generate_and_send_report')
def test_on_result_fetched(mock_generate_report, mock_send_to_user):
    # Create dummy RabbitMQ parameters (not used in logic).
    mock_channel = MagicMock()
    mock_method = MagicMock()
    mock_properties = MagicMock()

    # Define sample incoming message with a user_id.
    sample_message = {
        "job_type": "RESULT",
        "content": {
            "user_id": "user123",
            "total_sample_size": 20,
            "batch_size": 10,
            "metric_values": {
                "accuracy": {
                    "computed_value": 0.85,
                    "ideal_value": 1.0,
                    "range": [0.0, 1.0]
                },
                "precision": {
                    "computed_value": 0.15,
                    "ideal_value": 1.0,
                    "range": [0.0, 1.0]
                }
            }

        }

    }
    message_body = json.dumps(sample_message)

    # Set the expected report that generate_report should return.
    mock_report = {"summary": "Test Report"}
    mock_generate_report.return_value = mock_report

    # Call on_result_fetched for the first batch.
    on_result_fetched(mock_channel, mock_method, mock_properties, message_body)

    # After first call, a per-user aggregator should be created.
    aggregator = user_aggregators.get("user123")
    assert aggregator is not None, "Aggregator for user123 should be initialized."
    assert aggregator.total_sample_size == 20, "Total sample size should be set to 20."
    assert aggregator.samples_processed == 10, "Samples processed should be 10 after first batch."
    intermediate_metrics = aggregator.get_aggregated_metrics()

    # Verify that an intermediate metrics message was sent.
    mock_send_to_user.assert_any_call("user123", aggregator_intermediate_metrics_log(intermediate_metrics))

    # Simulate processing the second (final) batch.
    on_result_fetched(mock_channel, mock_method, mock_properties, message_body)

    # Allow the reporting thread a moment to start.
    time.sleep(0.1)

    # Verify that completion and final report messages were sent.
    calls = mock_send_to_user.call_args_list
    completion_called = any(call[0][1] == aggregator_metrics_completion_log() for call in calls)
    # final_called = any(call[0][1] == aggregator_final_report_log(mock_report) for call in calls)
    assert completion_called, "Completion log was not sent."
    # assert final_called, "Final report log was not sent."
    # Ensure the per-user aggregator is cleaned up after completion.
    assert "user123" not in user_aggregators, "Aggregator for user123 should be removed after processing."


@patch('aggregator.aggregator.manager.send_to_user')
def test_websocket_handler(mock_send_to_user):
    # Create a dummy websocket that returns a user_id and supports iteration.
    class DummyWebsocket:
        def __init__(self, user_id):
            self.user_id = user_id
            self.sent_messages = []
            self.iterated = False

        def recv(self):
            return self.user_id

        def send(self, message):
            self.sent_messages.append(message)

        def __iter__(self):
            if not self.iterated:
                self.iterated = True
                yield "dummy"
            else:
                return iter([])

    user_id = "user456"
    dummy_ws = DummyWebsocket(user_id)

    # Call the websocket handler.
    websocket_handler(dummy_ws)

    # After the handler finishes, the user should be disconnected.
    assert user_id not in manager.active_connections


def test_send_to_clients_no_clients():
    # Mock message
    mock_message = "Test Message"
    mesg = aggregator_intermediate_metrics_log(mock_message)

    # Reset connected clients
    connected_clients.clear()

    # Call function under test
    send_to_clients(mesg)

    # Ensure message is stored in the queue
    assert message_queue.qsize() == 1


def test_send_to_clients_with_clients():
    # Mock WebSocket clients
    mock_client1 = MagicMock()
    mock_client2 = MagicMock()
    connected_clients.clear()
    connected_clients.add(mock_client1)
    connected_clients.add(mock_client2)

    # Mock message
    mock_message = "Test Message"
    mesg = aggregator_intermediate_metrics_log(mock_message)

    # Call function under test
    send_to_clients(mesg)

    # Ensure message is sent to all clients
    mock_client1.send.assert_called_once()
    mock_client2.send.assert_called_once()


# @patch("aggregator.aggregator.aggregator_generate_report")
# def test_aggregate_report(mock_generate_report):
#     # Mock metrics data
#     metrics = {"accuracy": 0.85, "precision": 0.15}

#     # Mock report generation functions
#     mock_generate_report.return_value = {"properties" : [], "info" : {}}
#     with patch.dict("os.environ", {"GOOGLE_GEMINI_API_KEY": "test_value"}):
#         # Call function under test
#         report = generate_and_send_report("mock_uuid", metrics, metrics_aggregator)

#         # Ensure report is generated correctly
#         assert "properties" in report
#         assert "info" in report
#         mock_generate_report.assert_called_once_with(metrics, "test_value")


def test_generate_and_send_report():
    aggregates = {
        "accuracy": {
            "computed_value": 0.85,
            "ideal_value": 1.0,
            "range": [0.0, 1.0]
        },
        "precision": {
            "computed_value": 0.15,
            "ideal_value": 1.0,
            "range": [0.0, 1.0]
        }
    }

    aggregator = MagicMock()

    with patch("aggregator.aggregator.aggregator_generate_report", new_callable=MagicMock) as mock_rep_gen, \
         patch.object(manager, "send_to_user") as mock_send_to_user:
        # Call function under test

        mock_return_report = {"properties": [], "info": {}}
        mock_rep_gen.return_value = mock_return_report

        generate_and_send_report("user123", aggregates, aggregator)

        # Ensure aggregator_generate_report is called
        mock_rep_gen.assert_called_once_with(aggregates, aggregator)
        mock_send_to_user.assert_called_once_with("user123", aggregator_final_report_log(mock_return_report))


@patch("aggregator.aggregator.get_legislation_extracts")
@patch("aggregator.aggregator.add_llm_insights")
def test_aggregator_generate_report(mock_add_llm_insights, mock_get_legislation_extracts):
    # Mock metrics data
    metrics = {"accuracy": 0.85, "precision": 0.15}

    # Mock report generation functions
    mock_get_legislation_extracts.return_value = []
    mock_add_llm_insights.return_value = []

    aggregator = MagicMock()
    aggregator.total_sample_size = 20

    # Call function under test
    report = aggregator_generate_report(metrics, aggregator)

    # Ensure report is generated correctly
    assert "properties" in report
    assert "info" in report
    mock_get_legislation_extracts.assert_called_once()
    mock_add_llm_insights.assert_called_once()


@pytest.mark.skip(reason="Skip due to API rate limit issues during deployment")
@patch.dict("os.environ", {"GOOGLE_GEMINI_API_KEY": "test_api_key"})
def test_get_api_key_from_env():
    api_key = get_api_key()
    assert api_key == "test_api_key"


@pytest.mark.skip(reason="Skip due to API rate limit issues during deployment")
@patch("builtins.open", new_callable=mock_open, read_data="file_api_key")
@patch.dict("os.environ", {"GOOGLE_GEMINI_API_KEY_FILE": "/path/to/api_key_file"})
def test_get_api_key_from_file(mock_file):
    api_key = get_api_key()
    mock_file.assert_called_once_with("/path/to/api_key_file")
    assert api_key == "file_api_key"


@patch.dict("os.environ", {}, clear=True)
def test_get_api_key_no_key():
    api_key = get_api_key()
    assert api_key is None
