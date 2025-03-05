def redis_namespace(ns: str) -> str:
    """Prepend the key with the correct namespace for Redis to group keys used by aignostic"""
    return f"aignostic.{ns}"


def redis_key(ns: str, key: str) -> str:
    """
    Prepend the key with the correct namespace for Redis to group keys used by aignostic,
    and then the key you want to use itself.

    Example:
        redis_key("jobs", "123") -> "aignostic.jobs:123"
    """
    return f"{redis_namespace(ns)}:{key}"
