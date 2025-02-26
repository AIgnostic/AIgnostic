from metrics.models import CalculateRequest
from metrics.numerical_metrics import (
    explanation_stability_score,
    explanation_sparsity_score,
    explanation_fidelity_score
)
from metrics.ntg_metric_utils import ntg_lime


def masked_sentence_explainability_stability(info: CalculateRequest) -> float:
    """
    masked_sentence_explainability computes the "LIME" equivalent for a text input model by modelling disimilarity in
    the input features.
    """
    return explanation_stability_score(info, lime_fn=ntg_lime)


def masked_sentence_explainability_sparsity(info: CalculateRequest) -> float:
    """
    masked_sentence_explainability computes the "LIME" equivalent for a text input model by modelling disimilarity in
    the input features.
    """
    return explanation_sparsity_score(info, lime_fn=ntg_lime)


def masked_sentence_explainability_fidelity(info: CalculateRequest) -> float:
    """
    masked_sentence_explainability computes the "LIME" equivalent for a text input model by modelling disimilarity in
    the input features.
    """
    return explanation_fidelity_score(info, lime_fn=ntg_lime)