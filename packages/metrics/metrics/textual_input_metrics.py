from metrics.models import CalculateRequest
from metrics.numerical_metrics import (
    explanation_sparsity_score,
    explanation_fidelity_score
)
from metrics.exceptions import MetricsComputationException
from metrics.ntg_metric_utils import text_input_lime, generate_synonym_perturbations
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def expl_stability_text_input(info: CalculateRequest) -> float:
    """
    masked_sentence_explainability computes the "LIME" equivalent for a text input model by modelling disimilarity in
    the input features.
    """
    masked_coefs, _ =  text_input_lime(info)
    print("Running expl_stability_text_input")
    # TODO: Refactor generate_synonym_perturbations to take in an np.array of strings rather than a single string
    synonym_coefs = []
    masked_coefs_resized = []
    print(f"masked_coefs: {masked_coefs}")
    print(f"masked_coefs.shape: {masked_coefs.shape}")
    for i in range(info.input_features.shape[0]):
        # Obtain the text input string to the model
        inp = info.input_features[i][0]
        print(inp)
        
        # Obtain the confidence scores for the model
        targets = info.confidence_scores[i]

        # Generate synonym perturbations for one input at a time - shape = (num_perturbations, 1)
        synonym_sentences = np.array(generate_synonym_perturbations(inp)).reshape(-1, 1)

        # Obtain the LIME coefficients for the synonym perturbations
        temp_input_features = info.input_features
        temp_c_scores = info.confidence_scores

        # Duplicate the confidence scores for the synonym perturbations shape = (num_perturbations, c)
        # where c is the number classes in the model
        info.confidence_scores = np.array([[targets]] * synonym_sentences.shape[0])
        info.input_features = synonym_sentences
        
        mask_with_synonyms_coefs, _ = text_input_lime(info)

        # Append the LIME coefficients for the synonym perturbations to the list of coefficients
        synonym_coefs += mask_with_synonyms_coefs.tolist()
        # the coefficients for each of the original samples are the same when comparing between each perturbed sample
        # and the original sample
        masked_coefs_resized.append(masked_coefs.tolist())

        # Reset the input features and confidence scores to the original values after
        # obtaining the LIME coefficients for the synonym perturbations
        info.input_features = temp_input_features
        info.confidence_scores = temp_c_scores

    synonym_coefs = np.array(synonym_coefs)
    print(f"synonym_coefs: {synonym_coefs}")
    print(f"synonym_coefs.shape: {synonym_coefs.shape}")
    masked_coefs_resized = np.array(masked_coefs_resized)
    masked_coefs_resized.reshape(-1, masked_coefs_resized.shape[-1])
    print(f"masked_coefs_resized: {masked_coefs_resized}")
    print(f"masked_coefs_resized.shape: {masked_coefs_resized.shape}")

    # Obtain perturbed lime output

    # use cosine-similarity for now but can be replaced with model-provider function later
    # TODO: Took absolute value of cosine similarity - verify if this is correct
    diff = np.abs(cosine_similarity(synonym_coefs.reshape(-1, 1), masked_coefs_resized.reshape(-1, 1)))
    return 1 - np.mean(diff).item()


def expl_sparsity_text_input(info: CalculateRequest) -> float:
    """
    masked_sentence_explainability computes the "LIME" equivalent for a text input model by modelling disimilarity in
    the input features.
    """
    return explanation_sparsity_score(info, lime_fn=text_input_lime)


def expl_fidelity_text_input(info: CalculateRequest) -> float:
    """
    masked_sentence_explainability computes the "LIME" equivalent for a text input model by modelling disimilarity in
    the input features.
    """
    return explanation_fidelity_score(info, lime_fn=text_input_lime)