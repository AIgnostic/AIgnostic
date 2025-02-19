import numpy as np


def nested_list_to_np(value) -> np.array:
    if value:
        return np.array(value)
    return value

def np_to_nested_list(value, model_name) -> list[list]:
    if value is not None and isinstance(value, np.ndarray):
        return value.tolist()
    return value