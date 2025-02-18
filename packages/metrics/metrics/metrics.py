"""
    This module contains the implementation of various metrics
    For now this is a placeholder for the metrics implementation
    Containing simply the accuracy, precision and recall metrics
    For a binary classification problem
"""

from typing import Callable
from metrics.models import (
    CalculateRequest,
    MetricValues,
)
from metrics.utils import (
    _query_model,
    _lime_explanation
    # _fgsm_attack,
)
from sklearn.metrics import (
    f1_score,
    roc_auc_score,
    mean_absolute_error as mae,
    mean_squared_error as mse,
    r2_score,
)
from aif360.metrics import ClassificationMetric
from aif360.datasets import BinaryLabelDataset
import pandas as pd
import numpy as np
from metrics.exceptions import MetricsException, ModelQueryException
from common.models import ModelInput, ModelResponse


def is_valid_for_per_class_metrics(metric_name, true_labels):
    """
    Check if the input is valid for the given metric. Valid fn for precision, recall and F1 scoring
    """
    if len(true_labels) == 0:
        raise MetricsException(
            metric_name,
            detail="No labels provided - will lead to division by zero",
        )
    elif len(true_labels[0]) > 1:
        raise MetricsException(
            metric_name,
            detail=f"Multiple attributes provided - cannot calculate {metric_name}",
        )
    elif len(true_labels[0]) == 0:
        raise MetricsException(
            metric_name,
            detail=f"No attributes provided - cannot calculate {metric_name}",
        )


"""
    Performance metrics
"""


def accuracy(name, info: CalculateRequest) -> float:
    """
    Calculate the accuracy of the model
    """
    try:
        return (info.true_labels == info.predicted_labels).mean()
    except Exception as e:
        # Catch exceptions generally for now rather than specific ones
        raise MetricsException(name, detail=str(e))


def _calculate_precision(metric_name, true_labels, predicted_labels, target_class):
    try:
        target_reshaped = np.full_like(true_labels, target_class)
        tp = np.count_nonzero(
            (true_labels == target_reshaped) & (predicted_labels == target_reshaped)
        )
        fp = np.count_nonzero(
            (true_labels != target_reshaped) & (predicted_labels == target_reshaped)
        )
        return tp / (tp + fp) if (tp + fp) != 0 else 0
    except (ValueError, TypeError) as e:
        raise MetricsException(metric_name, detail=str(e))


def class_precision(name, info: CalculateRequest) -> float:
    """
    Calculate the precision for a given class. The labels/predictions provided must only be for
    one attribute of the predictions. Calculating precisions for multiple attributes will raise
    an exception
    """
    is_valid_for_per_class_metrics(name, info.true_labels)
    return _calculate_precision(
        name, info.true_labels, info.predicted_labels, info.target_class
    )


def macro_precision(name, info: CalculateRequest) -> float:
    """
    Calculate the macro precision for all classes
    """
    is_valid_for_per_class_metrics(name, info.true_labels)
    return sum(
        [
            _calculate_precision(name, info.true_labels, info.predicted_labels, c)
            for c in np.unique(info.true_labels)
        ]
    ) / len(np.unique(info.true_labels))


def _calculate_recall(metric_name, true_labels, predicted_labels, target_class):
    try:
        target_reshaped = np.full_like(true_labels, target_class)
        tp = np.count_nonzero(
            (true_labels == target_reshaped) & (predicted_labels == target_reshaped)
        )
        fn = np.count_nonzero(
            (true_labels == target_reshaped) & (predicted_labels != target_reshaped)
        )
        return tp / (tp + fn) if (tp + fn) != 0 else 0
    except Exception as e:
        raise MetricsException(metric_name, detail=str(e))


def class_recall(name, info: CalculateRequest) -> float:
    """
    Calculate the recall for a given class. The labels/predictions provided must only be for
    one attribute of the predictions. Calculating recalls for multiple attributes will raise
    an exception
    """
    is_valid_for_per_class_metrics(name, info.true_labels)
    return _calculate_recall(
        name, info.true_labels, info.predicted_labels, info.target_class
    )


def macro_recall(name, info: CalculateRequest) -> float:
    """
    Calculate the macro recall for all classes
    """
    is_valid_for_per_class_metrics(name, info.true_labels)
    return sum(
        [
            _calculate_recall(name, info.true_labels, info.predicted_labels, c)
            for c in np.unique(info.true_labels)
        ]
    ) / len(np.unique(info.true_labels))


def class_f1(name, info: CalculateRequest) -> float:
    """
    Calculate the F1 score for a given class. The labels
    provided must only be for one attribute of the predictions.
    """
    is_valid_for_per_class_metrics(name, info.true_labels)
    return f1_score(info.true_labels, info.predicted_labels)


def macro_f1(name, info: CalculateRequest) -> float:
    """
    Calculate the macro F1 score for all classes
    """
    is_valid_for_per_class_metrics(name, info.true_labels)
    return f1_score(info.true_labels, info.predicted_labels, average="macro")


def roc_auc(name, info: CalculateRequest) -> float:
    """
    Calculate the ROC-AUC score.
    """
    is_valid_for_per_class_metrics(name, info.true_labels)
    return roc_auc_score(info.true_labels, info.predicted_labels)


def mean_absolute_error(name, info: CalculateRequest) -> float:
    """
    Calculate the Mean Absolute Error (MAE).
    """
    is_valid_for_per_class_metrics(name, info.true_labels)
    return mae(info.true_labels, info.predicted_labels)


def mean_squared_error(name, info: CalculateRequest) -> float:
    """
    Calculate the Mean Squared Error (MSE).
    """
    is_valid_for_per_class_metrics(name, info.true_labels)
    return mse(info.true_labels, info.predicted_labels)


def r_squared(name, info: CalculateRequest) -> float:
    """
    Calculate the R-squared score.
    """
    is_valid_for_per_class_metrics(name, info.true_labels)
    return r2_score(info.true_labels, info.predicted_labels)


def _prepare_datasets(info: CalculateRequest):
    """
    _prepare_datasets reformats the input data as required by aif360 library for fairness
    metric calculations.

    This function takes the true labels, predicted labels, and protected attributes from the
    CalculateRequest object and creates BinaryLabelDataset objects for both the true and predicted
    labels (as required by aif360). These datasets are then used to calculate various fairness metrics.

    :param info: CalculateRequest - contains the true labels, predicted labels, and protected attributes.
    :return: tuple - a tuple containing the true labels dataset and the predicted labels dataset.
    """
    true_labels = info.true_labels.flatten()
    predicted_labels = info.predicted_labels.flatten()

    if not hasattr(info, "protected_attr") or info.protected_attr is None:
        raise ValueError("protected_attr is missing from the request.")

    protected_attrs = info.protected_attr.flatten()
    df_true = pd.DataFrame({"label": true_labels, "protected_attr": protected_attrs})
    df_pred = pd.DataFrame(
        {"label": predicted_labels, "protected_attr": protected_attrs}
    )

    dataset = BinaryLabelDataset(
        df=df_true, label_names=["label"], protected_attribute_names=["protected_attr"]
    )
    classified_dataset = BinaryLabelDataset(
        df=df_pred, label_names=["label"], protected_attribute_names=["protected_attr"]
    )  # predictions
    return dataset, classified_dataset


"""
    Fairness metrics
"""


def equalized_odds_difference(name, info: CalculateRequest) -> float:
    """
    Compute equalized odds difference from a CalculateRequest.

    Args:
        request: CalculateRequest object containing true labels, predicted labels, and protected attribute.

    Calculates:
        fpr_diff: Absolute difference in false positive rates across groups.
        tpr_diff: Absolute difference in true positive rates across groups.

    Returns:
        float: Equalized odds difference (absolute difference in fpr_diff and tpr_diff).
    """

    is_valid_for_per_class_metrics(name, info.true_labels)

    if info.true_labels is None or info.predicted_labels is None or info.protected_attr is None:
        raise ValueError("Missing required fields: true_labels, predicted_labels, or protected_attr")

    labels = info.true_labels
    predictions = info.predicted_labels
    groups = np.array(info.protected_attr)

    def rate(target_label, group):
        """Compute TPR or FPR based on the target class and group."""
        try:
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
        except Exception as e:
            raise MetricsException(name, detail=str(e))

    try:
        fpr_1 = rate(0, 1)  # False positive rate for group 1
        fpr_0 = rate(0, 0)  # False positive rate for group 0
        tpr_1 = rate(1, 1)  # True positive rate for group 1
        tpr_0 = rate(1, 0)  # True positive rate for group 0

        return abs(abs(fpr_1 - fpr_0) - abs(tpr_1 - tpr_0))
    except Exception as e:
        raise MetricsException(name, detail=str(e))


def create_fairness_metric_fn(metric_fn: Callable[[ClassificationMetric], float]) -> Callable:
    """
    create_fairness_metric_fn generates the function to calculate a specific fairness metric.
    The function in question validates the HTTPRequest input, and generates the function (callable)
    to calculate the fairness metric.

    :param metric_fn: Callable[[ClassificationMetric], float] - a function that takes list of
      ClassificationMetric objects and returns a metric value of type float (i.e. metric output)
    :return: Callable - a function that takes the name of the metric and information required in
      calculations. A function is returned for lazy evaluation.
    """
    def wrapper(name: str, info: CalculateRequest) -> float:
        """
        :param: name: str - name of the metric being calculated
        :param: info: CalculateRequest - contains information required to calculate the metric
        """
        try:
            dataset, classified_dataset = _prepare_datasets(info)
            metric = ClassificationMetric(
                dataset,
                classified_dataset,
                privileged_groups=info.privileged_groups,
                unprivileged_groups=info.unprivileged_groups,
            )

            metrics = metric_fn(metric)

        except Exception as e:
            raise MetricsException(name, detail=str(e))

        if np.isnan(metrics):
            raise MetricsException(
                    name,
                    detail="Output of Metric Calculation is NaN (expected a float)",
                )
        return metrics

    return wrapper


"""
    Uncertainty metrics
"""


async def ood_auroc(name, info: CalculateRequest, num_ood_samples: int = 1000) -> float:
    """
    Estimate OOD AUROC by comparing in-distribution (ID) and out-of-distribution (OOD)
    confidence scores.

    Args:
        info: CalculateRequest object containing input data, confidence scores, model URL, and model API key.
        num_ood_samples: Number of OOD samples to generate.

    Returns :
        auroc: Estimated OOD AUROC score.
    """
    if info.input_features is None:
        raise MetricsException(name, detail="Input data is required.")

    if info.confidence_scores is None:
        raise MetricsException(name, detail="Confidence scores are required.")

    id_data: np.array = np.array(info.input_features)   # In-distribution dataset (N x d array).
    d: int = id_data.shape[1]                       # Feature dimensionality

    id_scores: list[list] = info.confidence_scores  # Confidence scores for ID samples

    # Generate OOD samples
    id_min, id_max = id_data.min(axis=0), id_data.max(axis=0)
    ood_data = np.random.uniform(id_min, id_max, size=(num_ood_samples, d))

    # Construct dictionary for model input (labels and group_ids are not required)
    generated_input = ModelInput(
        features=ood_data.tolist(),
        labels=np.zeros((num_ood_samples, 1)).tolist(),
        group_ids=np.zeros(num_ood_samples, dtype=int).tolist(),
    )

    # Call model endpoint to get confidence scores
    response: ModelResponse = await _query_model(generated_input, info)

    # Get confidence scores for OOD samples
    if response.confidence_scores is None:
        raise ModelQueryException(name, detail="Model response did not contain confidence scores, which are required.")
    ood_scores: list[list] = response.confidence_scores

    # Construct labels: 1 for ID, 0 for OOD
    labels = np.concatenate([np.ones(len(id_scores)), np.zeros(num_ood_samples)])

    # Flatten the confidence scores for both ID and OOD samples
    scores = np.concatenate([np.array(id_scores).flatten(), np.array(ood_scores).flatten()])

    # Check if lengths match
    if len(labels) != len(scores):
        raise MetricsException(name, detail="Length mismatch between labels and scores.")

    return roc_auc_score(labels, scores)


"""
    Explainability metrics
"""


def explanation_stability_score(name, info: CalculateRequest) -> float:
    """
    Calculate the explanation stability score for a given model and sample inputs

    :param name: str - name of the metric being calculated
    :param info: CalculateRequest - contains information required to calculate the metric.
        explanation_stability_score requires the input_features, model_url and model_api_key.

    :return: float - the explanation stability score (1 - 1/N * sum(distance_fn(E(x), E(x')))
        where distance_fn is the distance function between two explanations E(x) and E(x')
    """
    # TODO: Replace with actual distance fn or endpoint once impl finalised
    def distance_fn(x, y) -> float:
        return np.linalg.norm(x - y)

    lime_actual, _ = _lime_explanation(info)
    lime_perturbed, _ = _lime_explanation(info)

    diff = distance_fn(lime_actual, lime_perturbed)
    return 1 - np.mean(diff).item()


def explanation_sparsity_score(name, info: CalculateRequest) -> float:
    """
    Calculate the explanation sparsity score for a given model and sample inputs

    :param name: str - name of the metric being calculated
    :param info: CalculateRequest - contains information required to calculate the metric.
        explanation_sparsity_score requires the input_features, model_url and model_api_key.

    :return: float - the explanation sparsity score (1 - sparsity_fn(E(x)))
        where sparsity_fn is || E(x) ||_0 / d - number of non-zero elements in the explanation
        divided by the total number of features
    """
    lime_explanation, _ = _lime_explanation(info)
    sparsity = np.count_nonzero(lime_explanation) / lime_explanation.shape[1]
    return 1 - sparsity


def explanation_fidelity_score(name, info: CalculateRequest) -> float:
    """
    Calculate the explanation fidelity score for a given model and sample inputs

    :param name: str - name of the metric being calculated
    :param info: CalculateRequest - contains information required to calculate the metric.
        explanation_fidelity_score requires the input_features, predicted_labels, model_url
        and model_api_key.

    :return: float - the explanation fidelity score (1 - 1/N * fidelity_fn(f(x), g(x))) where
        fidelity_fn is the distance function between the model output f(x) and the output of
        an interpretable approximation g(x) of the model
    """
    _, reg_model = _lime_explanation(info)

    # TODO: Update fidelity_fn implementation after discussion with supervisor
    def fidelity_fn(x, y) -> float:
        return np.linalg.norm(x - y)

    return 1 - np.mean(
        fidelity_fn(
            info.predicted_labels,
            reg_model.predict(info.input_features)
        )).item()


metric_to_fn = {
    "accuracy": accuracy,
    "class_precision": class_precision,
    "precision": macro_precision,
    "class_recall": class_recall,
    "recall": macro_recall,
    "class_f1_score": class_f1,
    "f1_score": macro_f1,
    "roc_auc": roc_auc,
    "mean_absolute_error": mean_absolute_error,
    "mean_squared_error": mean_squared_error,
    "r_squared": r_squared,
    "equalized_odds_difference": equalized_odds_difference,
    **{
        metric_name: create_fairness_metric_fn(
            # name=metric_name needed here otherwise metric_name will be captured by the lambda once
            lambda metric, name=metric_name: getattr(metric, name)()
        )
        for metric_name in [                    # aif360 fairness metrics
            "statistical_parity_difference",    # demographic parity
            "equal_opportunity_difference",
            "disparate_impact",
            "false_negative_rate_difference",
            "negative_predictive_value",
            "positive_predictive_value",
            "true_positive_rate_difference",
        ]
    },
    "ood_auroc": ood_auroc,
    "explanation_stability_score": explanation_stability_score,
    "explanation_sparsity_score": explanation_sparsity_score,
    "explanation_fidelity_score": explanation_fidelity_score,
}
""" Mapping of metric names to their corresponding functions"""


async def calculate_metrics(info: CalculateRequest) -> MetricValues:
    """
    calculate_metrics, given a request for calculation of certain metrics and information
    necessary for calculation, attempt to calculate and return the metrics and their scores
    for the given model and dataset.

    :param info: CalculateRequest - contains list of metrics to be calculated and additional
    data required for calculation of these metrics.
    :return: MetricValues - contains the calculated metrics and their scores
    """
    results = {}
    for metric in info.metrics:
        if metric not in metric_to_fn.keys():
            results[metric] = 1
        else:
            results[metric] = await metric_to_fn[metric](metric, info)
    return MetricValues(metric_values=results)
