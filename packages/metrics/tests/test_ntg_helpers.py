from metrics.ntg_metric_utils import generate_synonym_perturbations


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
