# How do I extend the metrics library with my own custom metric?

The metrics library is designed to be extensible, allowing you to add your own custom metrics to the library. This guide will walk you through the process of adding a custom metric to the library.

#


Each metric function should take a CalculateRequest object as input and return a float. The CalculateRequest object contains the following fields:

```python
class CalculateRequest(BaseModel):
    metrics: list[str]
    task_name: Optional[TaskName]
    batch_size: Optional[int]
    input_features: Optional[list[list]]
    confidence_scores: Optional[list[list]]
    true_labels: Optional[list[list]]
    predicted_labels: Optional[list[list]]
    target_class: Optional[Any]
    privileged_groups: Optional[list[dict[str, Any]]]
    unprivileged_groups: Optional[list[dict[str, Any]]]
    protected_attr: Optional[list[int]]
    model_url: Optional[HttpUrl]
    model_api_key: Optional[str]
```
Note that even though most of the expected attributes are 'Optional', the metric function should check for the presence of the required attributes before proceeding with the calculation.

The TaskName Enum consists of the following:
```python
class TaskType(str, Enum):
    BINARY_CLASSIFICATION = "binary_classification"
    MULTI_CLASS_CLASSIFICATION = "multi_class_classification"
    TEXT_CLASSIFICATION = "text_classification"
    REGRESSION = "regression"
    NEXT_TOKEN_GENERATION = "next_token_generation"

```

#### Step 1: Create a new metric

Below is a sample implementation of a custom metric function. This function calculates the Equalized Odds Difference metric.

```python
def equalized_odds_difference(info: CalculateRequest) -> float:
    """
    Compute equalized odds difference from a CalculateRequest.

    :param info: CalculateRequest - contains information required to calculate the metric.
        equalized_odds_difference requires true_labels, predicted_labels, and protected_attr.

    :return: float - the equalized odds difference
    """
    name = "equalized_odds_difference"
    is_valid_for_per_class_metrics(name, info.true_labels)

    labels = info.true_labels
    predictions = info.predicted_labels
    groups = np.array(info.protected_attr)

    def rate(target_label, group):
        """Compute TPR or FPR based on the target class and group."""
        # Select only data belonging to the current group (group mask)
        group_mask = (groups == group)

        # Filter the labels, predictions, and groups for the current group
        group_labels = labels[group_mask]
        group_predictions = predictions[group_mask]

        if target_label == 1:
            # True Positive Rate (TPR) -> TP / (TP + FN)
            tp = np.count_nonzero((group_labels == 1) & (group_predictions == 1))
            fn = np.count_nonzero((group_labels == 1) & (group_predictions == 0))
            total = tp + fn
        else:
            # False Positive Rate (FPR) -> FP / (FP + TN)
            fp = np.count_nonzero((group_labels == 0) & (group_predictions == 1))
            tn = np.count_nonzero((group_labels == 0) & (group_predictions == 0))
            total = fp + tn

        if total == 0:
            return 0.0
        return tp / total if target_label == 1 else fp / total

    fpr_1 = rate(0, 1)  # False positive rate for group 1
    fpr_0 = rate(0, 0)  # False positive rate for group 0
    tpr_1 = rate(1, 1)  # True positive rate for group 1
    tpr_0 = rate(1, 0)  # True positive rate for group 0

    return abs(abs(fpr_1 - fpr_0) - abs(tpr_1 - tpr_0))
```

The 'is_valid_for_per_class_metrics' function is used to check if the metric is valid for per-class metrics. This function is defined in the 'metrics/utils.py' file.

#### Step 2: Register the new metric in the metric mappings

Each of our metric functions are stored in a dictionary (metric_to_fn_and_requirements), with the string name of the metric as the key and a dictionary containing the function, required inputs, range, and ideal value as the value.

```python
metric_to_fn_and_requirements["equalized_odds_difference"] = {
    "function": equalized_odds_difference,
    "required_inputs": ["true_labels", "predicted_labels", "protected_attr"],
    "range": (0, 1),
    "ideal_value": 0.0
}
```

Note that:
#
> \> 'required_inputs' should contain the list of attributes that the metric function expects in the CalculateRequest object
#
> \> 'range' should define the metric's possible values (e.g., (0, 1) for a metric between 0 and 1, or None for an infinite range). If None is the first value, the range extends from negative infinity to the second value; if it's the second value, the range extends from the first value to positive infinity
#
> \> 'ideal_value' should define the ideal value of the metric as a float

#

Moreover, the 'task_type_to_metric' dictionary maps the task type to the metrics that are valid for that task type. If the metric is valid for all task types, it must be added to all the model types.

```python
task_type_to_metric[TaskType.BINARY_CLASSIFICATION] = [
    "accuracy",
    "balanced_accuracy",
    "equalized_odds_difference"
]
```