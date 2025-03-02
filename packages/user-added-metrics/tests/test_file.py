
from typing import Any, Optional
from pydantic import BaseModel, Field, HttpUrl
from pydantic import BaseModel, field_validator, HttpUrl, Field
import numpy as np



def metric_custom_accuracy(data: dict) -> dict:
    """
    Calculate the accuracy of the model.

    :param data: dict - Dictionary containing required inputs.
        - "true_labels": List or NumPy array of true labels.
        - "predicted_labels": List or NumPy array of predicted labels.

    :return: dict - Dictionary containing computed accuracy, ideal value, and range.
    """
    true_labels = np.array(data.get("true_labels"))
    predicted_labels = np.array(data.get("predicted_labels"))

    if true_labels.shape != predicted_labels.shape:
        raise ValueError("Shape mismatch: true_labels and predicted_labels must have the same shape.")

    accuracy = (true_labels == predicted_labels).mean()
    ideal_accuracy = 1.0
    accuracy_range = (0.0, 1.0)

    return {
        "computed_value": accuracy,
        "ideal_value": ideal_accuracy,
        "range": accuracy_range
    }


def metric_custom_equalized_odds_difference(data: dict) -> dict:
    """
    Compute equalized odds difference from a dictionary.

    :param data: dict - Dictionary containing required inputs.
        equalized_odds_difference requires true_labels, predicted_labels, and protected_attr.

    :return: dict - Dictionary containing the equalized odds difference.
    """
    labels = np.array(data.get("true_labels"))
    predictions = np.array(data.get("predicted_labels"))
    groups = np.array(data.get("protected_attr"))

    def rate(target_label, group):
        """Compute TPR or FPR based on the target class and group."""
        group_mask = (groups == group)
        group_labels = labels[group_mask]
        group_predictions = predictions[group_mask]

        if target_label == 1:
            tp = np.count_nonzero((group_labels == 1) & (group_predictions == 1))
            fn = np.count_nonzero((group_labels == 1) & (group_predictions == 0))
            total = tp + fn
        else:
            fp = np.count_nonzero((group_labels == 0) & (group_predictions == 1))
            tn = np.count_nonzero((group_labels == 0) & (group_predictions == 0))
            total = fp + tn

        if total == 0:
            return 0.0
        return tp / total if target_label == 1 else fp / total

    fpr_1 = rate(0, 1)
    fpr_0 = rate(0, 0)
    tpr_1 = rate(1, 1)
    tpr_0 = rate(1, 0)

    equalized_odds_diff = abs(abs(fpr_1 - fpr_0) - abs(tpr_1 - tpr_0))
    ideal_equalized_odds_diff = 0.0
    equalized_odds_diff_range = (-1 , 1.0)

    return {
        "computed_value": equalized_odds_diff,
        "ideal_value": ideal_equalized_odds_diff,
        "range": equalized_odds_diff_range
    }