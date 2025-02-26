import nltk
from nltk.corpus import wordnet as wn
from nltk.translate.bleu_score import sentence_bleu
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from rouge import Rouge
import editdistance


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

# TODO: Implement BERT_score computation (Facing poetry dependency issues with 2.6.0+cpu version of torch)
