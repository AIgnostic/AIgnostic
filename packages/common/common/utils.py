import numpy as np


def nested_list_to_np(value: list[list]) -> np.array:
    if value:
        return np.array(value)
    return value
