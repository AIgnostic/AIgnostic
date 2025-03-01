"""Constants for RabbitMQ interactions"""

JOB_QUEUE = "job_queue"
"""Queue where jobs for evaluation are placed"""
BATCH_QUEUE = "batch_queue"
"""Queue where batches are placed for picking up by workers"""
RESULT_QUEUE = "result_queue"
"""Queue where results are placed"""
