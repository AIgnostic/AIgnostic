import numpy as np

def nested_list_to_np(value):
    if value:
        return np.array(value)
    return value