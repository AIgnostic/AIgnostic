import nltk
from nltk.corpus import wordnet as wn
from nltk.translate.bleu_score import sentence_bleu
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from rouge import Rouge
import editdistance
from metrics.models import CalculateRequest, TaskType
from metrics.exceptions import (
    MetricsComputationException,
    InvalidParameterException,
    ModelQueryException,
    DataProvisionException
)
from random import sample
from metrics.utils import (
    _query_model
)
from common.models import ModelResponse
from sklearn.linear_model import Ridge
from math import ceil
from sentence_transformers import SentenceTransformer
import torch
import random

MIN_AVERAGE_SENTENCE_LENGTH = 4
MASK_WORD = "[MASK]"
DEFAULT_ENCODER = "sentence-transformers/distiluse-base-multilingual-cased-v1"

nltk.download('wordnet')


def generate_random_strings(num_samples: int, word_count: int = 10) -> np.array:
    """Generates `num_samples` random strings, each with `word_count` words from WordNet."""

    # Get all WordNet words
    words = list(set(word.lemma_names()[0] for word in wn.all_synsets()))

    # Generate random sentences
    strs = [
        " ".join(random.choices(words, k=word_count)) for _ in range(num_samples)
    ]

    return np.array(strs)


def generate_synonym_perturbations(sentence: str, mask=MASK_WORD, limit=10) -> list[str]:
    """
    Given a sentence, generate a list of sentences where one word is replaced by a synonym.
    """
    # Download WordNet data if not already present
    words = sentence.split()
    perturbations = []
    for i, word in enumerate(words):
        if word == mask:
            continue
        # Retrieve synonyms from WordNet, excluding the original word
        synonyms = {lemma.name().replace('_', ' ') for syn in wn.synsets(word)
                    for lemma in syn.lemmas() if lemma.name().lower() != word.lower()}
        # Create a new sentence for each synonym substitution
        for syn in synonyms:
            perturbed_words = words.copy()
            perturbed_words[i] = syn
            perturbed_sentence = " ".join(perturbed_words)
            perturbations.append(perturbed_sentence)
    # TODO: Sample in a more effective way than random sampling
    perturbations = sample(perturbations, min(limit, len(perturbations)))
    return perturbations


def embedding_perturbation_cosine_similarities(embeddings: np.array, embeddings_perturbed: np.array) -> np.array:
    """
    Given two batches of sentence embeddings, where one represents model inputs and the other represents
    perturbed model inputs, calculate the sentence embedding between each pair, returned as an np array
    of shape (N, 1).

    :param embeddings: np.array - Sentence embeddings for the original sentences (2D np.array)
    :param embedding_perturbed: np.array - Sentence embedding for the perturbed sentence (2D np.array)

    :return: np.array - Cosine similarity between the sentence embeddings (2D np.array)
    """
    similarities = cosine_similarity(embeddings, embeddings_perturbed)
    return np.diagonal(similarities).reshape(-1, 1)


def prompt_to_embeddings(prompts: np.array, encoder_path=DEFAULT_ENCODER) -> np.array:
    """
    Given a list of prompts, convert them to sentence embeddings using a semantically aligned
    sentence encoder model.

    :param prompts: np.array - List of prompts (1D or 2D input) - valid shapes: (N,) or (N, 1)
    :param encoder_name: str - Name of the sentence encoder model to use, default = "LaBSE"

    :return: np.array - Sentence embeddings (2D np.array)
    """
    model = SentenceTransformer(f"{encoder_path}")
    if prompts.ndim == 2:
        if prompts.shape[1] != 1:
            raise DataProvisionException(
                detail=(
                    "Input datapoints must be singleton string arrays representing one prompt"
                )
            )
        prompts = prompts.flatten()
    elif prompts.ndim != 1:
        raise DataProvisionException(
            detail="Input features must be a 1D or 2D array of text samples",
        )

    batch_size = 5
    num_prompts = len(prompts)
    embeddings = np.zeros((num_prompts, model.get_sentence_embedding_dimension()))
    for i in range(0, num_prompts, batch_size):
        batch_end = min(i + batch_size, num_prompts)
        with torch.no_grad():
            embeddings[i:i+batch_end] = model.encode(prompts[i:i+batch_end], normalize_embeddings=True)
    return embeddings


def prompt_perturbation_cosine_similarities(
    input_sentences: np.array, perturbed_sentences: np.array,
    encoder_name=DEFAULT_ENCODER
) -> np.array:
    """
    Given two lists of input and perturbed sentences, calculate the cosine similarity between the sentence embeddings.
    Use a semantically aligned sentence embedding model to compute the embeddings.

    :param input_sentences: np.array - List of input sentences
    :param perturbed_sentences: np.array - List of perturbed sentences
    :param encoder_name: str - Name of the sentence encoder model to use, default = "LaBSE"

    :return: np.array - Cosine similarity between the sentence embeddings (2D np.array)
    """

    embeddings = prompt_to_embeddings(input_sentences, encoder_name)
    embeddings_perturbed = prompt_to_embeddings(perturbed_sentences, encoder_name)

    return embedding_perturbation_cosine_similarities(embeddings, embeddings_perturbed)


# TODO: Write tests
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


# TODO: Write tests
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


# TODO: Write tests
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


# TODO: Write tests
def compute_bert_scores(target_sentences: list[str], perturbed_sentences: list[str]) -> list[float]:
    """
    Given two lists of target and perturbed sentences, calculate the BERT score for each pair.

    :param target_sentences: list[str] - List of target sentences
    :param perturbed_sentences: list[str] - List of perturbed sentences

    :return: list[float] - List of BERT scores
    """
    pass


def generate_masked_sequences(sentences: np.array, mask_prob: float = 0.3, num_masked_per_sentence=10) -> np.array:
    """
    Given a batch of sentences, generate masked sequences by randomly masking words. This approach is
    preferred to masking every word one at a time as this scales with the length of the input.

    :param sentences: np.array - Array of sentences to be masked, shape = (num_sentences, 1)
    :param mask_prob: float - Probability of masking a word
    :param num_masked_per_sentence: int - Number of masked sequences to generate per sentence,
        default = 10

    :return: np.array - Array of masked sequences. Note, if an output sentence is the same as the
        input sentence, it will be re-generated until at least one word is masked.
        shape = (num_sentences, num_masked_per_sentence)
    """
    if mask_prob <= 0 or mask_prob >= 1:
        raise InvalidParameterException(
            detail="masking probability must be greater than 0 and less than 1",
        )

    if num_masked_per_sentence <= 0:
        raise InvalidParameterException(
            detail="Number of masked sequences per sentence must be greater than 0",
        )

    masked_sequences = np.full((sentences.shape[0], num_masked_per_sentence), sentences, dtype=list)

    def mask_sentence(sentence: str) -> str:
        words = sentence.split()
        for i in range(len(words)):
            if np.random.rand() < mask_prob:
                words[i] = MASK_WORD
        out = " ".join(words)
        if out == sentence:
            return mask_sentence(sentence)
        return out

    sentence_mask = np.vectorize(mask_sentence)
    for i in range(num_masked_per_sentence):
        masked_sequences[:, i] = np.array([sentence_mask(s[0]) for s in sentences])
    return masked_sequences


def text_input_lime(info: CalculateRequest) -> tuple[np.array, Ridge]:
    """
    ntg_explainability_masking computes the "LIME" equivalent for a text input model by modelling disimilarity in
    probability scores between the original and perturbed samples. "Perturbations" are generated by masking individual
    words rather than the using normal distributions as in traditional LIME computation.
    """
    print("Running text_input_lime")
    print(f"info.input_features.shape: {info.input_features.shape}")
    _, d = info.input_features.shape
    # Each datapoint can only be a single sentence input
    if d != 1:
        raise MetricsComputationException(
            metric_name="ntg-explainability",
            detail="Input features must be a 1D array of text samples"
        )

    # Generate masked sequences for each sentence
    # Choose number of generated masked texts to be proportional to the average sentence length
    average_sentence_length = ceil(np.mean([len(sentence.split()) for sentence in info.input_features.reshape(-1)]))
    print(f"average_sentence_length: {average_sentence_length}")
    print(f"info.input_features: {info.input_features}")
    # If average sentence length is too short, raise an exception - it is better to
    # raise a warning in the frontend about potentially inaccurate metrics
    if average_sentence_length <= MIN_AVERAGE_SENTENCE_LENGTH:
        raise DataProvisionException(
            detail="Insufficient number of words in each input sequence to accurately"
            " compute metrics requiring masked sequences",
        )

    # Generation of the N masked sequences per sentence where N is proportional to the average sentence length
    perturbed_samples = generate_masked_sequences(
        info.input_features,
        num_masked_per_sentence=ceil(average_sentence_length / 10)
    )
    # Required later to map inputs to masked inputs
    num_perturbations_per_sample = perturbed_samples.shape[1]
    # Flatten the array and reshape to 2D (convert from (N, 10) to (N*10, 1))
    # This allows us to query the model API with all perturbed samples at once in a way
    # that is compatible with the expected implementation
    perturbed_samples = np.array(perturbed_samples).reshape(-1).reshape(-1, 1)
    # TODO: Consider batching inputs to the model API
    response: ModelResponse = _query_model(perturbed_samples, info)
    # If output is regression, use predictions, otherwise use confidence scores for classification
    # outputs.shape = (num_samples * num_perturbations_per_sample, 1) if regression
    # outputs.shape = (num_samples * num_perturbations_per_sample, num_classes) if classification
    outputs = (
        response.predictions
        if info.task_name in [TaskType.NEXT_TOKEN_GENERATION, TaskType.REGRESSION]
        else response.confidence_scores
    )

    print("info.task_name: ", info.task_name)

    if info.task_name not in [TaskType.NEXT_TOKEN_GENERATION, TaskType.REGRESSION]:
        if outputs is None:
            raise ModelQueryException(
                detail="NOT NEXT TOKEN GENERATION",
                status_code=400
            )

    # outputs should only be None if it we use confidence_scores as pydantic enforces predictions are present
    if outputs is None:
        raise ModelQueryException(
            detail="Model response does not contain probability scores for outputs",
            status_code=400
        )

    if info.task_name == TaskType.NEXT_TOKEN_GENERATION:
        # convert to embeddings
        outputs = prompt_to_embeddings(np.array(outputs))

    # Convert input features to shape (N * num_perturbations_per_sample, d) from (N, 1)
    # where d is either the number of classes for classification or 1 for regression
    features = np.tile(info.input_features, (num_perturbations_per_sample, 1))

    feature_embeddings = prompt_to_embeddings(features)
    perturbed_embeddings = prompt_to_embeddings(perturbed_samples)

    # Choose cosine similarity for text inputs as they involve large embedding spaces
    cosine_similarities = embedding_perturbation_cosine_similarities(feature_embeddings, perturbed_embeddings)
    # Small constant for numerical stability
    epsilon = 1e-10

    # TODO: Investigate choice of kernel width
    kernel_width = np.sqrt(info.input_features.shape[0]) * 0.75

    # normal distribution kernel
    weights = np.exp(-cosine_similarities ** 2 / (2 * kernel_width ** 2)) + epsilon
    weights = weights.flatten()

    # Fit a weighted linear regression model
    reg_model = Ridge(alpha=1.0)

    reg_model.fit(perturbed_embeddings - feature_embeddings, outputs, sample_weight=weights)

    return reg_model.coef_, reg_model

# TODO: Implement a method to convert sentences to a fixed-length embedding space for semantic comparison. e.g. SONAR
