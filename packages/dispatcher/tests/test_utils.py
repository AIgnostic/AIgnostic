from dispatcher.utils import redis_key


def test_redis_key_gives_expected_format():
    assert redis_key("jobs", "123") == "aignostic.jobs:123"
