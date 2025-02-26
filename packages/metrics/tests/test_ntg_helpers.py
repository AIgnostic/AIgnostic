from metrics.ntg_metric_utils import (
    generate_synonym_perturbations,
    generate_masked_sequences
)
import numpy as np
from metrics.exceptions import InvalidParameterException
import pytest


def test_generate_synonym_perturbations_produces_perturbations():
    perturbations = generate_synonym_perturbations("Hello there")
    assert len(perturbations) == 9
    assert sorted(perturbations) == [
        "Hello at that place",
        "Hello in that location",
        "Hello in that respect",
        "Hello on that point",
        "Hello thither",
        "hi there",
        "how-do-you-do there",
        "howdy there",
        "hullo there"
    ]


def test_generating_perturbations_on_empty_inputs_generates_empty_list():
    perturbations = generate_synonym_perturbations("")
    assert len(perturbations) == 0
    assert perturbations == []


def test_perturbations_on_single_word():
    perturbations = generate_synonym_perturbations("Hello")
    assert len(perturbations) == 4
    assert sorted(perturbations) == [
        "hi",
        "how-do-you-do",
        "howdy",
        "hullo"
    ]


def test_generating_masked_sequences_does_not_duplicate_input():
    sentences = np.array([["This is a test sentence"], ["It was the best of times. It was the worst of times."]])
    masked_sequences = generate_masked_sequences(sentences, num_masked_per_sentence=10)
    assert masked_sequences.shape == (2, 10), f"Expected shape (2, 10), but got {masked_sequences.shape}"
    assert np.all(np.vectorize(lambda x: "[MASK]" in x)(masked_sequences)), "Expected [MASK] tokens in all masked sequences"


def test_invalid_mask_probability_raises_invalid_parameter_exception():
    sentences = np.array([["This is a test sentence"], ["It was the best of times. It was the worst of times."]])
    with pytest.raises(InvalidParameterException) as e:
        generate_masked_sequences(sentences, mask_prob=0, num_masked_per_sentence=10)


# TODO: Add lime tests for regression and classification for ntg_lime
