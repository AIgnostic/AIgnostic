import nltk
from nltk.corpus import wordnet as wn

# Download WordNet data if not already present
nltk.download('wordnet')

def generate_synonym_perturbations(sentence: str):
    """
    Given a sentence, generate a list of sentences where one word is replaced by a synonym.
    """
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

# Example usage:
original_sentence = "Hello there"
perturbed_queries = generate_synonym_perturbations(original_sentence)
print("Perturbations:", perturbed_queries)