# Test we can load up all the models without errors


from common.models.pipeline import MetricCalculationJob


def test_can_import_and_init_common_models():
    import common.models.common  # noqa: F401


def test_can_import_and_init_pipeline_models():
    import common.models.pipeline  # noqa: F401


def test_total_sample_size_should_be_multiplication():
    from common.models.pipeline import PipelineJob

    job = PipelineJob(
        batches=10,
        batch_size=50,
        job_id="123",
        max_concurrent_batches=3,
        metrics=MetricCalculationJob(
            data_url="http://localhost:8000",
            model_url="http://localhost:8000",
            data_api_key="",
            model_api_key="",
            metrics=["accuracy"],
            model_type="classification",
        ),
    )
    assert job.total_sample_size == 500
