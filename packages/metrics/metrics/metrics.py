"""
    This module contains the implementation of various metrics
    For now this is a placeholder for the metrics implementation
    Containing simply the accuracy, precision and recall metrics
    For a binary classification problem
"""

# TODO: Update pydocs for regression tasks

from typing import Callable
from metrics.models import (
    CalculateRequest,
    MetricValue,
    MetricConfig,
)
from metrics.utils import (
    _query_model,
    _lime_explanation,
    _finite_difference_gradient
)
from sklearn.metrics import (
    f1_score,
    roc_auc_score,
    mean_absolute_error as mae,
    mean_squared_error as mse,
    r2_score,
)
from sklearn.metrics.pairwise import cosine_similarity
from aif360.metrics import ClassificationMetric
from aif360.datasets import BinaryLabelDataset
import pandas as pd
import numpy as np
from metrics.exceptions import (
    MetricsComputationException,
    DataInconsistencyException,
    DataProvisionException,
    _MetricsPackageException
)
from common.models import ModelResponse


task_type_to_metric = {
    "binary_classification": [
        "accuracy",
        "precision",
        "recall",
        "f1_score",
        "roc_auc",
        "statistical_parity_difference",
        "equal_opportunity_difference",
        "equalized_odds_difference",
        "disparate_impact",
        "false_negative_rate_difference",
        "negative_predictive_value",
        "positive_predictive_value",
        "true_positive_rate_difference",
        # "explanation_stability_score",
        # "explanation_sparsity_score",
        # "explanation_fidelity_score",
        # "ood_auroc",
    ],
    "multi_class_classification": [
        "accuracy",
        # "class_precision",
        "precision",
        # "class_recall",
        "recall",
        # "class_f1_score",
        "f1_score",
        "roc_auc",
        # "explanation_stability_score",
        # "explanation_sparsity_score",
        # "explanation_fidelity_score",
        # "ood_auroc",
    ],
    "regression": [
        "mean_absolute_error",
        "mean_squared_error",
        "r_squared",
        # "explanation_stability_score",
        # "explanation_sparsity_score",
        # "explanation_fidelity_score",
    ],
}
"""
    This mapping of model types to metrics is used to provide information about the types
    of metrics that can be calculated for each model type, and is passed to the frontend
    for selection of metrics based on the model type.

    When adding new metrics, ensure that they are added to the appropriate model type.
"""


def is_valid_for_per_class_metrics(metric_name, true_labels):
    """
    Check if the input is valid for the given metric. Valid fn for precision, recall and F1 scoring

    :param metric_name: str - name of the metric being calculated for error handling
    :param true_labels: np.array - the true labels for the dataset

    :raises MetricsException: if the input is invalid for the given metric
    :return: None
    """
    if len(true_labels) == 0:
        raise DataProvisionException(
            detail=f"No labels provided - will lead to division by zero for {metric_name}",
            status_code=400,
        )
    elif len(true_labels[0]) > 1:
        raise MetricsComputationException(
            metric_name,
            detail=f"Multiple attributes provided - cannot calculate {metric_name}",
            status_code=400,
        )
    elif len(true_labels[0]) == 0:
        raise DataProvisionException(
            detail=f"No attributes provided - cannot calculate {metric_name}",
            status_code=400,
        )
    return


"""
    Performance metrics
"""


def accuracy(info: CalculateRequest) -> float:
    """
    Calculate the accuracy of the model

    :param info: CalculateRequest - contains information required to calculate the metric.
        accuracy requires true_labels and predicted_labels to be provided.
    """
    return (info.true_labels == info.predicted_labels).mean()


def _calculate_precision(metric_name, true_labels, predicted_labels, target_class):
    """
    Apply the precision formula to the given data

    :param metric_name: str - name of the metric being calculated for error handling
    :param true_labels: np.array - the true labels for the dataset
    :param predicted_labels: np.array - the predicted labels for the dataset
    :param target_class: int - the class for which precision is being calculated

    :raises MetricsException: if the input is invalid for the given metric
    :return: float - the precision score for the given class
    """
    target_reshaped = np.full_like(true_labels, target_class)
    tp = np.count_nonzero(
        (true_labels == target_reshaped) & (predicted_labels == target_reshaped)
    )
    fp = np.count_nonzero(
        (true_labels != target_reshaped) & (predicted_labels == target_reshaped)
    )
    return tp / (tp + fp) if (tp + fp) != 0 else 0


def class_precision(info: CalculateRequest) -> float:
    """
    Calculate the precision for a given class. The labels/predictions provided must only be for
    one attribute of the predictions. Calculating precisions for multiple attributes will raise
    an exception

    :param info: CalculateRequest - contains information required to calculate the metric.
        class_precision requires true_labels, predicted_labels and target_class to be provided.

    :return: float - the precision score for the given class
    """
    name = "class_precision"
    is_valid_for_per_class_metrics(name, info.true_labels)
    return _calculate_precision(
        name, info.true_labels, info.predicted_labels, info.target_class
    )


def macro_precision(info: CalculateRequest) -> float:
    """
    Calculate the macro precision for all classes

    :param info: CalculateRequest - contains information required to calculate the metric.
        macro_precision requires true_labels and predicted_labels to be provided.

    :return: float - the macro precision score for all classes
    """
    name = "macro_precision"
    is_valid_for_per_class_metrics(name, info.true_labels)
    return sum(
        [
            _calculate_precision(name, info.true_labels, info.predicted_labels, c)
            for c in np.unique(info.true_labels)
        ]
    ) / len(np.unique(info.true_labels))


def _calculate_recall(metric_name, true_labels, predicted_labels, target_class):
    """
    Apply the recall formula to the given data

    :param metric_name: str - name of the metric being calculated for error handling
    :param true_labels: np.array - the true labels for the dataset
    :param predicted_labels: np.array - the predicted labels for the dataset
    :param target_class: int - the class for which recall is being calculated

    :raises MetricsException: if the input is invalid for the given metric
    :return: float - the recall score for the given class
    """
    target_reshaped = np.full_like(true_labels, target_class)
    tp = np.count_nonzero(
        (true_labels == target_reshaped) & (predicted_labels == target_reshaped)
    )
    fn = np.count_nonzero(
        (true_labels == target_reshaped) & (predicted_labels != target_reshaped)
    )
    return tp / (tp + fn) if (tp + fn) != 0 else 0


def class_recall(info: CalculateRequest) -> float:
    """
    Calculate the recall for a given class. The labels/predictions provided must only be for
    one attribute of the predictions. Calculating recalls for multiple attributes will raise
    an exception

    :param info: CalculateRequest - contains information required to calculate the metric.
        class_recall requires true_labels, predicted_labels and target_class to be provided.

    :return: float - the recall score for the given class
    """
    name = "class_recall"
    is_valid_for_per_class_metrics(name, info.true_labels)
    return _calculate_recall(
        name, info.true_labels, info.predicted_labels, info.target_class
    )


def macro_recall(info: CalculateRequest) -> float:
    """
    Calculate the macro recall for all classes

    :param info: CalculateRequest - contains information required to calculate the metric.
        macro_recall requires true_labels and predicted_labels to be provided.

    :return: float - the macro recall score for all classes
    """
    name = "macro_recall"
    is_valid_for_per_class_metrics(name, info.true_labels)
    return sum(
        [
            _calculate_recall(name, info.true_labels, info.predicted_labels, c)
            for c in np.unique(info.true_labels)
        ]
    ) / len(np.unique(info.true_labels))


# TODO: Check if this function is even required as it's not any new functionality for the library
# It can also be replaced with macro_f1 in almost all cases
def class_f1(info: CalculateRequest) -> float:
    """
    Calculate the F1 score for a given class. The labels
    provided must only be for one attribute of the predictions.

    :param info: CalculateRequest - contains information required to calculate the metric.
        class_f1 requires true_labels and predicted_labels to be provided.

    :return: float - the F1 score for the given class
    """
    name = "class_f1"
    is_valid_for_per_class_metrics(name, info.true_labels)
    # TODO: Check if this is the correct way to calculate F1 score for a single class
    return f1_score(info.true_labels, info.predicted_labels)


def macro_f1(info: CalculateRequest) -> float:
    """
    Calculate the macro F1 score for all classes

    :param info: CalculateRequest - contains information required to calculate the metric.
        macro_f1 requires true_labels and predicted_labels to be provided.

    :return: float - the macro F1 score for all classes
    """
    name = "macro_f1"
    is_valid_for_per_class_metrics(name, info.true_labels)
    return f1_score(info.true_labels, info.predicted_labels, average="macro")


def roc_auc(info: CalculateRequest) -> float:
    """
    Calculate the ROC-AUC score.

    :param info: CalculateRequest - contains information required to calculate the metric.
        roc_auc requires true_labels and predicted_labels to be provided.

    :return: float - the ROC-AUC score
    """
    name = "roc_auc"
    is_valid_for_per_class_metrics(name, info.true_labels)
    return roc_auc_score(info.true_labels, info.predicted_labels, average="macro", multi_class="ovr")


def mean_absolute_error(info: CalculateRequest) -> float:
    """
    Calculate the Mean Absolute Error (MAE).

    :param info: CalculateRequest - contains information required to calculate the metric.
        mean_absolute_error requires true_labels and predicted_labels to be provided.

    :return: float - the MAE score
    """
    return mae(info.true_labels, info.predicted_labels)


def mean_squared_error(info: CalculateRequest) -> float:
    """
    Calculate the Mean Squared Error (MSE).

    :param info: CalculateRequest - contains information required to calculate the metric.
        mean_squared_error requires true_labels and predicted_labels to be provided.

    :return: float - the MSE score
    """
    return mse(info.true_labels, info.predicted_labels)


def r_squared(info: CalculateRequest) -> float:
    """
    Calculate the R-squared score.

    :param info: CalculateRequest - contains information required to calculate the metric.
        r_squared requires true_labels and predicted_labels to be provided.

    :return: float - the R-squared score given by 1 - (sum of squares of residuals /
        sum of squares of total)
    """
    return r2_score(info.true_labels, info.predicted_labels)


def _prepare_datasets(info: CalculateRequest):
    """
    _prepare_datasets reformats the input data as required by aif360 library for fairness
    metric calculations.

    This function takes the true labels, predicted labels, and protected attributes from the
    CalculateRequest object and creates BinaryLabelDataset objects for both the true and predicted
    labels (as required by aif360). These datasets are then used to calculate various fairness metrics.

    :param info: CalculateRequest - requires non-empty true_labels, predicted_labels,
        and protected_attr.
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
    def wrapper(info: CalculateRequest) -> float:
        """
        :param: info: CalculateRequest - contains information required to calculate the metric.
            wrapper requires true_labels, predicted_labels, protected_attr, privileged_groups,
            and unprivileged_groups to be provided.

        :return: float - the calculated fairness metric value
        """
        dataset, classified_dataset = _prepare_datasets(info)
        metric = ClassificationMetric(
            dataset,
            classified_dataset,
            privileged_groups=info.privileged_groups,
            unprivileged_groups=info.unprivileged_groups,
        )

        metrics = metric_fn(metric)

        if np.isnan(metrics):
            # 0 returned to avoid division by zero errors
            # TODO: Only return 0 if division by zero has been identified
            return 0
        return metrics

    return wrapper


"""
    Explainability metrics
"""


def explanation_stability_score(info: CalculateRequest) -> float:
    """
    Calculate the explanation stability score for a given model and sample inputs

    :param info: CalculateRequest - contains information required to calculate the metric.
        explanation_stability_score requires the input_features, confidence_scores,
        model_url and model_api_key.

    :return: float - the explanation stability score (1 - 1/N * sum(distance_fn(E(x), E(x')))
        where distance_fn is the distance function between two explanations E(x) and E(x')
    """
    lime_actual, _ = _lime_explanation(info)

    # Calculate gradients for perturbation
    gradients = _finite_difference_gradient(info, 0.01)
    perturbation_constant = 0.01
    perturbation = perturbation_constant * gradients

    # Go in direction of greatest loss
    info.input_features = info.input_features + perturbation

    # Obtain perturbed lime output
    lime_perturbed, _ = _lime_explanation(info)

    # use cosine-similarity for now but can be replaced with model-provider function later
    # TODO: Took absolute value of cosine similarity - verify if this is correct
    diff = np.abs(cosine_similarity(lime_perturbed.reshape(1, -1), lime_actual.reshape(1, -1)))
    return 1 - np.mean(diff).item()


def explanation_sparsity_score(info: CalculateRequest) -> float:
    """
    Calculate the explanation sparsity score for a given model and sample inputs

    :param info: CalculateRequest - contains information required to calculate the metric.
        explanation_sparsity_score requires the input_features, confidence_scores, model_url
        and model_api_key.

    :return: float - the explanation sparsity score (1 - sparsity_fn(E(x)))
        where sparsity_fn is || E(x) ||_0 / d - number of coeffs within one standard deviation
        of the mean coefficients.
    """
    # Threshold for sparsity - defined arbitrarily for now
    # TODO: get mean and std of the *explanations* element-wise (per feature)
    #  - then check proportion less than 2 sigma from the mean
    # Note unnormalised inputs may have a volatile stability scores due to varying gradients
    # leading to greater variations in mean and std
    lime_explanation_coeffs, _ = _lime_explanation(info, esp=True)
    mean = np.mean(lime_explanation_coeffs)
    std = np.std(lime_explanation_coeffs)

    print(f"info: {info}")

    # Number of coefficients greater than 2 sigma from the mean
    count_far_from_mean = np.sum(np.abs(lime_explanation_coeffs - mean) > std)
    print(f"mean: {mean}, std: {std}, count_far_from_mean: {count_far_from_mean}")
    print(f"coeffs: {lime_explanation_coeffs}")
    print(f"count: {count_far_from_mean}")

    return 1 - count_far_from_mean / len(lime_explanation_coeffs)


def explanation_fidelity_score(info: CalculateRequest) -> float:
    """
    Calculate the explanation fidelity score for a given model and sample inputs.

    :param info: CalculateRequest - contains information required to calculate the metric.
        explanation_fidelity_score requires the input_features, confidence_scores, model_url
        and model_api_key.

    :return: float - the explanation fidelity score (1 - 1/N * fidelity_fn(f(x), g(x))) where
        fidelity_fn is the distance function between the model output f(x) and the output of
        an interpretable approximation g(x) of the model. For classification tasks, confidence_scores
        (probabilities) are compared instead.
    """
    _, reg_model = _lime_explanation(info)

    # regression model predicts *probability* not prediction (after updating lime explanation)

    # TODO: Update fidelity_fn implementation after discussion with supervisor
    # Used L-1 Norm for now -> using L2 norm may mean we have to divide by sqrt(N) instead of N
    def fidelity_fn(x, y) -> float:
        return np.linalg.norm(x - y, 1)

    print(info.confidence_scores)
    ps = reg_model.predict(info.input_features).reshape(-1, 1)
    print(ps)
    print(fidelity_fn(info.confidence_scores, ps))
    print(f"len info.confidence_scores: {len(info.confidence_scores)}")
    subtracted = fidelity_fn(info.confidence_scores, ps) / len(info.confidence_scores)
    print(f"subtracted: {subtracted}")
    return 1 - subtracted


"""
    Uncertainty metrics
"""


def ood_auroc(info: CalculateRequest, num_ood_samples: int = 1000) -> float:
    """
    Estimate OOD AUROC by comparing in-distribution (ID) and out-of-distribution (OOD)
    confidence scores.

    :param info: CalculateRequest - contains information required to calculate the metric.
        ood_auroc requires input_features, confidence_scores, model_url, and model_api_key.
    :param num_ood_samples: int - number of OOD samples to generate.

    :return: float - the estimated OOD AUROC score
    """
    id_data: np.array = np.array(info.input_features)   # In-distribution dataset (N x d array).
    d: int = id_data.shape[1]                       # Feature dimensionality

    id_scores: list[list] = info.confidence_scores  # Confidence scores for ID samples

    # Generate OOD samples
    id_min, id_max = id_data.min(axis=0), id_data.max(axis=0)
    ood_data = np.random.uniform(id_min, id_max, size=(num_ood_samples, d))

    # Call model endpoint to get confidence scores
    response: ModelResponse = _query_model(ood_data, info)

    # Get confidence scores for OOD samples
    ood_scores: list[list] = response.confidence_scores

    # Construct labels: 1 for ID, 0 for OOD
    labels = np.concatenate([np.ones(len(id_scores)), np.zeros(num_ood_samples)])

    # Flatten the confidence scores for both ID and OOD samples
    scores = np.concatenate([np.array(id_scores).flatten(), np.array(ood_scores).flatten()])

    # Assert lengths match
    assert len(labels) == len(scores), "Length mismatch between labels and scores in OOD-AUROC calculation."

    return roc_auc_score(labels, scores)


# Define metric properties for aif360 fairness metrics
metric_properties = {
    "statistical_parity_difference": {"range": (-1, 1), "ideal_value": 0},
    "equal_opportunity_difference": {"range": (-1, 1), "ideal_value": 0},
    "disparate_impact": {"range": (0, None), "ideal_value": 1},
    "false_negative_rate_difference": {"range": (-1, 1), "ideal_value": 0},
    "negative_predictive_value": {"range": (0, 1), "ideal_value": 0.8},
    "positive_predictive_value": {"range": (0, 1), "ideal_value": 0.8},
    "true_positive_rate_difference": {"range": (-1, 1), "ideal_value": 0}
}


""" Mapping of metric names to their corresponding functions and required inputs"""
metric_to_fn_and_requirements = {
    # Performance metrics
    "accuracy": {
        "function": accuracy,
        "required_inputs": ["true_labels", "predicted_labels"],
        "range": (0, 1),
        "ideal_value": 0.8
    },
    "class_precision": {
        "function": class_precision,
        "required_inputs": ["true_labels", "predicted_labels", "target_class"],
        "range": (0, 1),
        "ideal_value": 0.8
    },
    "precision": {
        "function": macro_precision,
        "required_inputs": ["true_labels", "predicted_labels"],
        "range": (0, 1),
        "ideal_value": 0.8
    },
    "class_recall": {
        "function": class_recall,
        "required_inputs": ["true_labels", "predicted_labels", "target_class"],
        "range": (0, 1),
        "ideal_value": 0.8
    },
    "recall": {
        "function": macro_recall,
        "required_inputs": ["true_labels", "predicted_labels"],
        "range": (0, 1),
        "ideal_value": 0.8
    },
    "class_f1_score": {
        "function": class_f1,
        "required_inputs": ["true_labels", "predicted_labels"],
        "range": (0, 1),
        "ideal_value": 0.8
    },
    "f1_score": {
        "function": macro_f1,
        "required_inputs": ["true_labels", "predicted_labels"],
        "range": (0, 1),
        "ideal_value": 0.8
    },
    "roc_auc": {
        "function": roc_auc,
        "required_inputs": ["true_labels", "predicted_labels"],
        "range": (0, 1),
        "ideal_value": 0.8
    },
    "mean_absolute_error": {
        "function": mean_absolute_error,
        "required_inputs": ["true_labels", "predicted_labels"],
        "range": (0, None),
        "ideal_value": 0
    },
    "mean_squared_error": {
        "function": mean_squared_error,
        "required_inputs": ["true_labels", "predicted_labels"],
        "range": (0, None),
        "ideal_value": 0
    },
    "r_squared": {
        "function": r_squared,
        "required_inputs": ["true_labels", "predicted_labels"],
        "range": (None, 1),
        "ideal_value": 0.7
    },

    # Fairness metrics
    **{
        metric_name: {
            "function": create_fairness_metric_fn(
                lambda metric, name=metric_name: getattr(metric, name)()
            ),
            "required_inputs": [
                "true_labels",
                "predicted_labels",
                "protected_attr",
                "privileged_groups",
                "unprivileged_groups"
            ],
            "range": metric_properties[metric_name]["range"],
            "ideal_value": metric_properties[metric_name]["ideal_value"]
        }
        for metric_name in metric_properties
    },
    "equalized_odds_difference": {
        "function": equalized_odds_difference,
        "required_inputs": ["true_labels", "predicted_labels", "protected_attr"],
        "range": (-1, 1),
        "ideal_value": 0
    },


    # Explainability metrics
    "explanation_stability_score": {
        "function": explanation_stability_score,
        "required_inputs": ["input_features", "confidence_scores", "model_url", "model_api_key"],
        "range": (0, 1),
        "ideal_value": 0.8
    },
    "explanation_sparsity_score": {
        "function": explanation_sparsity_score,
        "required_inputs": ["input_features", "confidence_scores", "model_url", "model_api_key"],
        "range": (0, 1),
        "ideal_value": 0.7
    },
    "explanation_fidelity_score": {
        "function": explanation_fidelity_score,
        "required_inputs": ["input_features", "confidence_scores", "model_url", "model_api_key"],
        "range": (0, 1),
        "ideal_value": 0.85
    },

    # Uncertainty metrics
    "ood_auroc": {
        "function": ood_auroc,
        "required_inputs": ["input_features", "confidence_scores", "model_url", "model_api_key"],
        "range": (0, 1),
        "ideal_value": 0.85
    },
}


def check_all_required_fields_present(metrics: set[str], info: CalculateRequest):
    """
    check_all_required_fields_present ensures that all the required fields are present in the
    CalculateRequest object.

    :param info: CalculateRequest - contains information required to calculate the metric.

    :return: None
    """
    metrics_to_exceptions = {}
    for metric in metrics:
        if metric not in metric_to_fn_and_requirements:
            metrics_to_exceptions[metric] = MetricsComputationException(
                metric,
                detail="Metric should be supported, but is not mapped to a computation. (Internal Error)"
            )
        else:
            missing_fields = []
            for field in metric_to_fn_and_requirements[metric]["required_inputs"]:
                if not hasattr(info, field) or getattr(info, field) is None:
                    missing_fields.append(field)
            if missing_fields:
                metrics_to_exceptions[metric] = DataProvisionException(
                    detail=f"The following missing fields are required to calculate metric {metric}:\n"
                           f"{missing_fields}"
                )
    return metrics_to_exceptions


def check_metrics_are_supported_for_task(info: CalculateRequest):
    """
    check_metrics_are_supported_for_task ensures that the metrics requested are supported
    for the task type provided.
    """
    if info.task_name not in task_type_to_metric:
        raise DataProvisionException(
            detail=f"Task {info.task_name} is not supported. Please choose a valid task."
        )

    invalid_metrics = set(info.metrics) - set(task_type_to_metric[info.task_name])
    metrics_to_exceptions = {}
    for metric in invalid_metrics:
        metrics_to_exceptions[metric] = MetricsComputationException(
            metric,
            detail=(
                f"Metric {metric} is not supported for {info.task_name} tasks."
                " Please only choose valid metrics for the task type."
                "\nSupported metrics for this task type are:\n"
                f" {task_type_to_metric[info.task_name]}"
            ),
            status_code=400
        )
    return metrics_to_exceptions


def calculate_metrics(info: CalculateRequest) -> MetricConfig:
    """
    calculate_metrics, given a request for calculation of certain metrics and information
    necessary for calculation, attempt to calculate and return the metrics and their scores
    for the given model and dataset.

    :param info: CalculateRequest - contains list of metrics to be calculated and additional
    data required for calculation of these metrics.
    :return: MetricConfig - contains the calculated metrics and their scores
    """
    current_metric = "calculate_metrics"

    # Input validation
    if info.confidence_scores is not None:
        if info.predicted_labels is not None:
            # If confidence scores and labels are both given, ensure they have the same length
            if info.confidence_scores.shape[0] != info.predicted_labels.shape[0]:
                raise DataInconsistencyException(
                    detail="Length mismatch between confidence scores and true labels.",
                )

    results = {}

    # Add all metrics to results if they raise an exception
    if info.task_name:
        results = check_metrics_are_supported_for_task(info)
        results = results | check_all_required_fields_present(
            set(info.metrics) - set(results.keys()),
            info
        )

    for metric in info.metrics:
        # Replace spaces with underscores in metric names to map to function names
        metric = metric.replace(" ", "_")
        try:
            # Skip the metric if it is known to throw an error
            if metric in results:
                continue

            # Store the current metric name for error handling
            current_metric = metric

            # Call the function for the metric and store the result
            metric_result = metric_to_fn_and_requirements[metric]["function"](info)

            # Store the result in the results object
            results[metric] = MetricValue(
                computed_value=metric_result,
                ideal_value=metric_to_fn_and_requirements[metric]["ideal_value"],
                range=metric_to_fn_and_requirements[metric]["range"]
            )

        # Return an exception in place of the metric result if applicable
        # Approach allows valid metrics to still be calculated
        except _MetricsPackageException as e:
            results[metric] = e
        except Exception as e:
            results[metric] = MetricsComputationException(current_metric, detail=str(e))
    return MetricConfig(
        metric_values=results,
        batch_size=info.batch_size,
        total_sample_size=info.total_sample_size
    )
