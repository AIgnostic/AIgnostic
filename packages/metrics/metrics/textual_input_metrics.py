from metrics.models import CalculateRequest
from metrics.numerical_metrics import (
    explanation_sparsity_score,
    explanation_fidelity_score
)
from metrics.ntg_metric_utils import text_input_lime, generate_synonym_perturbations
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def expl_stability_text_input(info: CalculateRequest) -> float:
    """
    masked_sentence_explainability computes the "LIME" equivalent for a text input model by modelling disimilarity in
    the input prompts. Currently, this is only supports text classification tasks.

    :param info: Information required to compute the gradient including info.input_features,
        confidence_scores, model_url and model_api_key.

    :return: Stability score for the model.
    """
    masked_coefs, _ = text_input_lime(info)
    print("Running expl_stability_text_input")
    # TODO: Refactor generate_synonym_perturbations to take in an np.array of strings rather than a single string
    synonym_coefs = []
    masked_coefs_resized = []
    for i in range(info.input_features.shape[0]):
        # Obtain the text input string to the model
        inp = info.input_features[i][0]

        print(f"task_name: {info.task_name}")
        # Obtain the confidence scores for the model
        if info.task_name in ['next_token_generation', 'regression']:
            targets = info.predicted_labels
        else:
            targets = info.confidence_scores
        print(f"targets: {targets}")

        # Generate synonym perturbations for one input at a time - shape = (num_perturbations, 1)
        synonym_sentences = np.array(generate_synonym_perturbations(inp)).reshape(-1, 1)

        # Obtain the LIME coefficients for the synonym perturbations
        temp_input_features = info.input_features

        temp_scores = targets
        # Duplicate the confidence scores for the synonym perturbations shape = (num_perturbations, c)
        # where c is the number classes in the model
        if info.task_name in ['next_token_generation', 'regression']:
            print(f"targets[i]: {targets[i]}")
            info.predicted_labels = np.array([targets[i]] * synonym_sentences.shape[0])
            assert info.predicted_labels.ndim == 2
        else:
            info.confidence_scores = np.array([targets[i]] * synonym_sentences.shape[0])
            assert info.confidence_scores.ndim == 2
        info.input_features = synonym_sentences
        print(f"synonym_sentences: {synonym_sentences}")
        mask_with_synonyms_coefs, _ = text_input_lime(info)
        print(f"mask_with_synonyms_coefs: {mask_with_synonyms_coefs}")

        # Append the LIME coefficients for the synonym perturbations to the list of coefficients
        synonym_coefs += mask_with_synonyms_coefs.tolist()
        # the coefficients for each of the original samples are the same when comparing between each perturbed sample
        # and the original sample
        masked_coefs_resized.append(masked_coefs.tolist())

        # Reset the input features and confidence scores to the original values after
        # obtaining the LIME coefficients for the synonym perturbations
        info.input_features = temp_input_features
        if info.task_name in ['next_token_generation', 'regression']:
            info.predicted_labels = temp_scores
        else:
            info.confidence_scores = temp_scores
        print(f"info.predicted_labels: {info.predicted_labels}")
        print(f"info.confidence_scores: {info.confidence_scores}")
        print(f"mask_with_synonyms_coefs.shape: {mask_with_synonyms_coefs.shape}")
    synonym_coefs = np.array(synonym_coefs)
    synonym_coefs = synonym_coefs.reshape(synonym_coefs.shape[0], -1)
    print(f"synonym_coefs.shape: {synonym_coefs.shape}")
    masked_coefs_resized = np.array(masked_coefs_resized)
    print(f"masked_coefs_resized.shape: {masked_coefs_resized.shape}")
    masked_coefs_resized = masked_coefs_resized.reshape(synonym_coefs.shape[0], -1)
    print(f"masked_coefs_resized.shape: {masked_coefs_resized.shape}")

    # Obtain perturbed lime output

    # use cosine-similarity for now but can be replaced with model-provider function later
    # TODO: Took absolute value of cosine similarity - verify if this is correct
    diff = np.abs(cosine_similarity(synonym_coefs, masked_coefs_resized))
    print(f"mean diff: {np.mean(diff)}")
    print(f"mean diff item: {np.mean(diff).item()}")
    print(f"1 - np.mean(diff).item(): {1 - np.mean(diff).item()}")
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