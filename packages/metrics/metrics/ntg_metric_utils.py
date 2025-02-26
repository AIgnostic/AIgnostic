import nltk
from nltk.corpus import wordnet as wn
from nltk.translate.bleu_score import sentence_bleu
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from rouge import Rouge
import editdistance
from metrics.models import CalculateRequest
from metrics.exceptions import (
    MetricsComputationException,
    InvalidParameterException,
    ModelQueryException
)
from metrics.utils import (
    _query_model
)
from common.models import ModelResponse
from scipy.spatial.distance import euclidean
from sklearn.linear_model import Ridge


def generate_synonym_perturbations(sentence: str):
    """
    Given a sentence, generate a list of sentences where one word is replaced by a synonym.
    """
    # Download WordNet data if not already present
    nltk.download('wordnet')

    words = sentence.split()
    perturbations = []
    for i, word in enumerate(words):
        # Retrieve synonyms from WordNet, excluding the original word
        synonyms = {lemma.name().replace('_', ' ') for syn in wn.synsets(word)
                    for lemma in syn.lemmas() if lemma.name().lower() != word.lower()}
        # Create a new sentence for each synonym substitution
        for syn in synonyms:
            perturbed_words = words.copy()
            perturbed_words[i] = syn
            perturbed_sentence = " ".join(perturbed_words)
            perturbations.append(perturbed_sentence)
    return perturbations


def compute_sentence_cosine_similarities(embeddings_target: np.array, embeddings_perturbed: np.array) -> np.array:
    """
    Given two sentence embeddings, calculate the cosine similarity between their word vectors.

    :param embedding_perturbed: np.array - Sentence embedding for the perturbed sentence (1D np.array)

    :return: np.array - Cosine similarity between the sentence embeddings
    """
    return cosine_similarity(embeddings_target, embeddings_perturbed)


def compute_batch_sentence_bleu(target_sentences: list[str], perturbed_sentences: list[str]) -> list[float]:
    """
    Given two lists of target and perturbed sentences, calculate the BLEU score for each pair.

    :param target_sentences: list[str] - List of target sentences
    :param perturbed_sentences: list[str] - List of perturbed sentences

    :return: list[float] - List of BLEU scores
    """
    bleu_scores = []
    for target, perturbed in zip(target_sentences, perturbed_sentences):
        bleu_scores.append(sentence_bleu([target.split()], perturbed.split()))
    return bleu_scores


def compute_batch_rouge_scores(target_sentences: list[str], perturbed_sentences: list[str]) -> list[float]:
    """
    Given two lists of target and perturbed sentences, calculate the ROUGE score for each pair.

    :param target_sentences: list[str] - List of target sentences
    :param perturbed_sentences: list[str] - List of perturbed sentences

    :return: list[float] - List of ROUGE scores
    """
    rouge = Rouge()
    scores = rouge.get_scores(target_sentences, perturbed_sentences)
    return scores


def compute_edit_distances(target_sentences: list[str], perturbed_sentences: list[str]) -> list[int]:
    """
    Given two lists of target and perturbed sentences, calculate the edit distance for each pair.

    :param target_sentences: list[str] - List of target sentences
    :param perturbed_sentences: list[str] - List of perturbed sentences

    :return: list[int] - List of edit distances
    """
    edit_distances = []
    for target, perturbed in zip(target_sentences, perturbed_sentences):
        edit_distances.append(editdistance.eval(target, perturbed))
    return edit_distances


# TODO
def compute_bert_scores(target_sentences: list[str], perturbed_sentences: list[str]) -> list[float]:
    """
    Given two lists of target and perturbed sentences, calculate the BERT score for each pair.
    
    :param target_sentences: list[str] - List of target sentences
    :param perturbed_sentences: list[str] - List of perturbed sentences
    
    :return: list[float] - List of BERT scores
    """
    pass


def generate_masked_sequences(sentences: np.array, mask_prob: float = 0.15, num_masked_per_sentence=10) -> np.array:
    """
    Given a batch of sentences, generate masked sequences by randomly masking words. This approach is preferred to masking
    every word one at a time as this scales with the length of the input.

    :param sentences: np.array - Array of sentences to be masked, shape = (num_sentences, 1)
    :param mask_prob: float - Probability of masking a word
    :param num_masked_per_sentence: int - Number of masked sequences to generate per sentence,
        default = 10

    :return: np.array - Array of masked sequences. Note, if an output sentence is the same as the input sentence, it will be
        re-generated until at least one word is masked.
        shape = (num_sentences, num_masked_per_sentence)
    """
    if mask_prob <= 0 or mask_prob >= 1:
        raise InvalidParameterException(
            detail="masking probability must be greater than 0 and less than 1",
        )

    masked_sequences = np.full((sentences.shape[0], num_masked_per_sentence), sentences, dtype=list)

    def mask_sentence(sentence: str) -> str:
        words = sentence.split()
        for i in range(len(words)):
            if np.random.rand() < mask_prob:
                words[i] = "[MASK]"
        out = " ".join(words)
        if out == sentence:
            return mask_sentence(sentence)
        return out

    sentence_mask = np.vectorize(mask_sentence)
    for i in range(num_masked_per_sentence):
        masked_sequences[:, i] = np.array([sentence_mask(s[0]) for s in sentences])
    print(masked_sequences)
    return masked_sequences


def ntg_lime(info: CalculateRequest):
    """
    ntg_explainability_masking computes the "LIME" equivalent for a text input model by modelling disimilarity in
    probability scores between the original and perturbed samples. "Perturbations" are generated by masking individual
    words rather than the using normal distributions as in traditional LIME computation.
    """
    num_samples, d = info.input_features.shape

    if d != 1:
        raise MetricsComputationException(
            metric_name="ntg-explainability",
            detail="Input features must be a 1D array of text samples"
        )

    # TODO: Change to probabilities instead of probabilities
    # Need total softmax as we can identify if the class value changes
    #  e.g. 0.9 -> 0.1 means some other class higher p value

    # Binary -> Bernoulli Noise
    # Assume numeric values for now
    # TODO: Add support for categorical features
    perturb_sentences = np.vectorize(generate_synonym_perturbations)
    perturbed_samples = np.array(perturb_sentences(info.input_features))

    # Call model endpoint to get confidence scores
    response: ModelResponse = _query_model(perturbed_samples, info)

    # Use probabilities if the output is a classification model, otherwise use regression outputs directly
    outputs = response.predictions if info.regression_flag else response.confidence_scores

    if outputs is None:
        raise ModelQueryException(
            detail="Model response does not contain probability scores for outputs",
            status_code=400
        )

    # Compute similarity weights using an RBF kernel
    distances = np.array([euclidean(info.input_features[i], sample) for i, sample in enumerate(perturbed_samples)])

    epsilon = 1e-10     # Small constant for numerical stability (avoid division by zero)
    kernel_width = np.sqrt(info.input_features.shape[0]) * 0.75
    weights = np.exp(-distances ** 2 / (2 * kernel_width ** 2)) + epsilon

    # Fit a weighted linear regression model
    reg_model = Ridge(alpha=1.0)
    reg_model.fit(perturbed_samples - info.input_features, outputs, sample_weight=weights)
    return reg_model.coef_, reg_model