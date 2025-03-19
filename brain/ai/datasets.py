"""datasets.py: Contains the dataset classes for the ACE program.

This module contains the dataset classes for the ACE program, which are
used to load and preprocess data for training machine learning models.

classes:
- IntentDataset: A dataset for intent classification.
"""

import os
import json
from typing import Callable, Dict, List, Tuple, Optional

import torch
from torch.utils.data import Dataset

from brain.text.preprocessing import (
    build_vocab,
    tokenize,
    vectorize,
    build_embedding_vocab,
    vectorize_embeddings,
)


class IntentDataset(Dataset):
    """A dataset for intent classification."""

    def __init__(
        self,
        corpus_path: str = os.path.join("data", "ACECorpus.json"),
        max_length: int = 20,
        use_embedding: bool = False,
        tokenizer: Callable[[str], List[str]] = tokenize,
        vectorizer: Optional[
            Callable[[List[str], Dict[str, int], int], List[int]]
        ] = None,
        prebuilt_vocab: Optional[Dict[str, int]] = None,
    ) -> None:
        """Initializes the IntentDataset.

        Args:
            corpus_path: The path to the corpus JSON file.
            max_length: The maximum length of an utterance after tokenization and vectorization.
            use_embedding: Whether to use embeddings for vectorization.
            tokenizer: A function to tokenize utterances.
            vectorizer: A function to vectorize tokenized utterances.
            prebuilt_vocab: A prebuilt vocabulary dictionary.
        """
        self.max_length = max_length
        self.use_embedding = use_embedding
        self.tokenizer = tokenizer

        # Load the corpus data from the JSON file.
        self.corpus = self._load_corpus(corpus_path)

        # Prepare the intent labels and their corresponding indices.
        self.intent_labels, self.intent_to_idx = self._prepare_intent_labels()

        # Tokenize the utterances from the corpus.
        tokenized_data = self._tokenize_utterances()

        # Build the vocabulary based on the tokenized data.
        self.word_to_idx = self._build_vocabulary(tokenized_data, prebuilt_vocab)

        # Select the appropriate vectorizer function.
        self.vectorizer = self._select_vectorizer(vectorizer)

        # Vectorize the tokenized data using the selected vectorizer.
        self.data = self._vectorize_data(tokenized_data)

    def __len__(self) -> int:
        """Returns the number of items in the dataset."""
        return len(self.data)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """Returns the item at the given index.

        Args:
            idx: The index of the item to return.

        Returns:
            A tuple containing the vectorized utterance and the intent index.
        """
        return self.data[idx]

    def _load_corpus(self, corpus_path: str) -> dict:
        """Loads the corpus from the given path.

        Args:
            corpus_path: The path to the corpus JSON file.

        Returns:
            The loaded corpus as a dictionary.

        Raises:
            FileNotFoundError: If the corpus file is not found.
            ValueError: If the corpus file is not valid JSON.
        """
        try:
            with open(corpus_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Corpus file not found: {corpus_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in: {corpus_path}")

    def _prepare_intent_labels(self) -> Tuple[List[str], Dict[str, int]]:
        """Prepares the intent labels and their indices.

        Returns:
            A tuple containing the list of intent labels and the dictionary mapping labels to indices.
        """
        intent_labels = [intent["intent"] for intent in self.corpus["intents"]]
        intent_to_idx = {intent: idx for idx, intent in enumerate(intent_labels)}
        return intent_labels, intent_to_idx

    def _tokenize_utterances(self) -> List[Tuple[List[str], int]]:
        """Tokenizes the utterances in the corpus.

        Returns:
            A list of tuples, where each tuple contains the tokenized utterance and its intent index.
        """
        return [
            (self.tokenizer(utterance), self.intent_to_idx[intent["intent"]])
            for intent in self.corpus["intents"]
            for utterance in intent["utterances"]
        ]

    def _build_vocabulary(
        self,
        tokenized_data: List[Tuple[List[str], int]],
        prebuilt_vocab: Optional[Dict[str, int]],
    ) -> Dict[str, int]:
        """Builds the vocabulary from the tokenized data.

        Args:
            tokenized_data: The list of tokenized utterances.
            prebuilt_vocab: An optional prebuilt vocabulary.

        Returns:
            The vocabulary dictionary.
        """
        if prebuilt_vocab:
            return prebuilt_vocab
        elif self.use_embedding:
            return build_embedding_vocab([tokens for tokens, _ in tokenized_data])
        else:
            return build_vocab([tokens for tokens, _ in tokenized_data])

    def _select_vectorizer(
        self,
        vectorizer: Optional[Callable[[List[str], Dict[str, int], int], List[int]]],
    ) -> Callable[[List[str], Dict[str, int], int], List[int]]:
        """Selects the vectorizer to use.

        Args:
            vectorizer: An optional custom vectorizer function.

        Returns:
            The selected vectorizer function.
        """
        if vectorizer is not None:
            return vectorizer
        elif self.use_embedding:
            return vectorize_embeddings
        else:
            return vectorize

    def _vectorize_data(
        self, tokenized_data: List[Tuple[List[str], int]]
    ) -> List[Tuple[torch.Tensor, torch.Tensor]]:
        """Vectorizes the tokenized data.

        Args:
            tokenized_data: The list of tokenized utterances.

        Returns:
            A list of tuples, where each tuple contains the vectorized utterance and its intent index.
        """
        return [
            (
                torch.as_tensor(
                    self.vectorizer(tokens, self.word_to_idx, self.max_length),
                    dtype=torch.long,
                ),
                torch.as_tensor(intent_idx, dtype=torch.long),
            )
            for tokens, intent_idx in tokenized_data
        ]


if __name__ == "__main__":  # pragma: no cover

    from pprint import pprint

    print(" IntentDataset ".center(80, "="))
    dataset = IntentDataset(use_embedding=False)
    print(f"Dataset size: {len(dataset)}")
    print("Intent dict:")
    pprint(dataset.intent_to_idx)
    print(f"Vocab size: {len(dataset.word_to_idx)}")
    print("Vocab:")
    pprint(dataset.word_to_idx)
    print(f"Example: {dataset[0][0].size()}")
    pprint(dataset[0])
    print("=" * 80)
