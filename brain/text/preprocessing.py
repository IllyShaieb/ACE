"""preprocessing.py: Contains text preprocessing functions for machine
learning models.

This module provides functions for tokenization, vocabulary building, and
vectorization of text data, which are essential steps in preparing text
data for machine learning models.
"""

import spacy
import torch

nlp = spacy.load("en_core_web_md")


def tokenize(text: str, lowercase: bool = True) -> list[str]:
    """Takes in a string of text and returns a list of tokens.

    Args:
        text (str): The text to tokenize.
        lowercase (bool, optional): Whether to convert the text to lowercase.
                                    Defaults to True.

    Returns:
        list[str]: A list of tokens without trailing spaces.
    """
    if lowercase:
        text = text.lower()
    return [token.text for token in nlp(text) if not token.is_space]


def build_vocab(tokenized_texts: list[list[str]]) -> dict[str, int]:
    """Builds a vocabulary from a list of tokenized texts.

    Args:
        tokenized_texts (list[list[str]]): A list of lists of strings, where
            each inner list represents a tokenized text.

    Returns:
        dict[str, int]: A dictionary mapping tokens to their indices.
    """
    # Initialize a set to store unique tokens
    tokens = set()

    # Add tokens from each tokenized text to the set
    for token_list in tokenized_texts:
        tokens.update(token_list)

    # Create a dictionary mapping tokens to their indices using enumerate and
    # sorted to ensure consistent order.
    vocab = {"<PAD>": 0, "<UNK>": 1}
    vocab.update({token: idx + 2 for idx, token in enumerate(sorted(tokens))})

    return vocab


def vectorize(
    tokenized_text: list[str], vocab: dict[str, int], max_length: int = 128
) -> list[int]:
    """Converts a tokenized text into a vector representation.

    Args:
        tokenized_text (list[str]): A list of strings representing a tokenized
            text.
        vocab (dict[str, int]): A dictionary mapping tokens to their indices.
        max_length (int, optional): The maximum length of the vectorized text.
            Defaults to 128.

    Returns:
        list[int]: A list of integers representing the vectorized text.
    """
    vector = [vocab.get(token, vocab["<UNK>"]) for token in tokenized_text]
    padding = [vocab["<PAD>"]] * (max_length - len(vector))
    return vector[:max_length] + padding


def build_embedding_vocab(tokenized_texts: list[list[str]]) -> dict[str, torch.Tensor]:
    """Builds a vocabulary with embedding vectors from tokenized texts."""
    vocab = {}
    for token_list in tokenized_texts:
        for token in token_list:
            if token not in vocab:
                vocab[token] = torch.tensor(nlp(token).vector)
    return vocab


def vectorize_embeddings(
    token_list: list[str], vocab: dict[str, torch.Tensor], max_length: int
) -> torch.Tensor:
    """Vectorizes a token list using embedding vectors."""
    vectors = []
    for token in token_list:
        if token in vocab:
            vectors.append(vocab[token])
        else:
            vectors.append(
                torch.zeros(nlp.vocab.vectors_length)
            )  # out of vocab vector.
    vectors = vectors[:max_length]
    padding_length = max_length - len(vectors)
    vectors += [torch.zeros(nlp.vocab.vectors_length)] * padding_length
    return torch.stack(vectors)


if __name__ == "__main__":
    # Provide some examples to see each of the functions
    from pprint import pprint

    text = "Hello, world! This is a test."
    print("# Original Text")
    print(text)

    tokenized_text = tokenize(text)
    print("\n# Tokenized Text")
    pprint(tokenized_text)

    vocab = build_vocab([tokenized_text])
    print("\n# Vocabulary")
    pprint(vocab)

    vectorized_text = vectorize(tokenized_text, vocab, max_length=15)
    print("\n# Vectorized Text")
    pprint(vectorized_text)

    embedding_vocab = build_embedding_vocab([tokenized_text])
    print("\n# Embedding Vocabulary")
    pprint(embedding_vocab)

    vectorized_embeddings = vectorize_embeddings(
        tokenized_text, embedding_vocab, max_length=15
    )
    print("\n# Vectorized Embeddings")
    pprint(vectorized_embeddings)
    print(vectorized_embeddings.shape)
