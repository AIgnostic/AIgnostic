from metrics.models import CalculateRequest
from metrics.numerical_metrics import (
    explanation_stability_score,
    explanation_sparsity_score,
    explanation_fidelity_score
)
from metrics.ntg_metric_utils import ntg_lime


def expl_stability_text_input(info: CalculateRequest) -> float:
    """
    masked_sentence_explainability computes the "LIME" equivalent for a text input model by modelling disimilarity in
    the input features.
    """
    lime_actual, _ =  _lime_explanation(info)

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


def expl_sparsity_text_input(info: CalculateRequest) -> float:
    """
    masked_sentence_explainability computes the "LIME" equivalent for a text input model by modelling disimilarity in
    the input features.
    """
    return explanation_sparsity_score(info, lime_fn=ntg_lime)


def expl_fidelity_text_input(info: CalculateRequest) -> float:
    """
    masked_sentence_explainability computes the "LIME" equivalent for a text input model by modelling disimilarity in
    the input features.
    """
    return explanation_fidelity_score(info, lime_fn=ntg_lime)