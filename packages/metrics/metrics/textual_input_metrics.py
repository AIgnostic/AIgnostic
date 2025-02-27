from metrics.models import CalculateRequest
from metrics.numerical_metrics import (
    explanation_sparsity_score,
    explanation_fidelity_score
)
from metrics.exceptions import MetricsComputationException
from metrics.ntg_metric_utils import ntg_lime, generate_synonym_perturbations
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def expl_stability_text_input(info: CalculateRequest) -> float:
    """
    masked_sentence_explainability computes the "LIME" equivalent for a text input model by modelling disimilarity in
    the input features.
    """
    masking_weights, _ =  ntg_lime(info)

    # TODO: Refactor generate_synonym_perturbations to take in an np.array of strings rather than a single string
    syn_coefs = []
    act_coefs = []

    for i in range(info.input_features.shape[0]):
        inp = info.input_features[i][0]
        c_scores = info.confidence_scores[i]
        synonym_sentences = np.array(generate_synonym_perturbations(inp)).reshape(-1, 1)

        temp_input_features = info.input_features
        temp_c_scores = info.confidence_scores
        info.confidence_scores = np.array([c_scores] * synonym_sentences.shape[0])
        info.input_features = synonym_sentences
        
        mask_with_syn_weights, _ = ntg_lime(info)
        
        syn_coefs += mask_with_syn_weights.tolist()
        # the coefficients for each of the original samples are the same when comparing between each perturbed sample
        # and the original sample
        act_coefs += masking_weights.tolist() * (mask_with_syn_weights.shape[0] // masking_weights.shape[1])

        info.input_features = temp_input_features
        info.confidence_scores = temp_c_scores

    syn_coefs = np.array(syn_coefs)
    act_coefs = np.array(act_coefs)

    # Obtain perturbed lime output

    # use cosine-similarity for now but can be replaced with model-provider function later
    # TODO: Took absolute value of cosine similarity - verify if this is correct
    diff = np.abs(cosine_similarity(syn_coefs.reshape(1, -1), act_coefs.reshape(1, -1)))
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