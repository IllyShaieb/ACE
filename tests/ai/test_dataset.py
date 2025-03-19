"""test_datasets.py: Tests for the datasets module in the ACE program.

Ensures that the datasets in the ACE program work as expected, and that
the data loaded and processed is correct.
"""

import unittest
import os
import json

import torch
from torch.utils.data import Dataset

from brain.ai.datasets import IntentDataset
from brain.text.preprocessing import tokenize


class TestIntentDataset(unittest.TestCase):
    """Tests for the IntentDataset class."""

    def setUp(self):
        """Set up test data."""
        self.corpus_data = {
            "intents": [
                {
                    "intent": "intent1",
                    "utterances": ["example for intent1", "another for intent1"],
                },
                {
                    "intent": "intent2",
                    "utterances": ["example for intent2", "another for intent2"],
                },
            ]
        }
        with open("test_corpus.json", "w") as f:
            json.dump(self.corpus_data, f)

    def tearDown(self):
        """Clean up test data."""
        os.remove("test_corpus.json")

    def test_initialise_dataset(self):
        """Test that the dataset correctly loads the corpus from a valid JSON file."""
        dataset = IntentDataset("test_corpus.json")
        self.assertIsInstance(dataset, Dataset)

    def test_invalid_corpus_path(self):
        """Test that the dataset raises an error when passed an invalid path."""
        with self.assertRaises(FileNotFoundError):
            IntentDataset("invalid_path.json")

    def test_invalid_corpus_file(self):
        """Test that dataset raises an error when passed invalid json data."""
        with open("test_corpus.json", "w") as f:
            f.write("invalid json")
        with self.assertRaises(ValueError):
            IntentDataset("test_corpus.json")

    def test_length_method(self):
        """Test the __len__ method of IntentDataset.

        The length is the number examples in the corpus.
        """
        dataset = IntentDataset("test_corpus.json")
        self.assertEqual(
            len(dataset), 4, "Length must be the number of examples in the corpus"
        )

    def test_get_item_method(self):
        """Test the __getitem__ method of IntentDataset."""
        dataset = IntentDataset("test_corpus.json")
        sample, label = dataset[0]
        self.assertIsInstance(sample, torch.Tensor)
        self.assertIsInstance(label, torch.Tensor)
        self.assertEqual(sample.shape[0], 20)  # test max length is being used.

    def test_intent_labels(self):
        """Test that intent labels are correctly created."""
        dataset = IntentDataset("test_corpus.json")
        self.assertEqual(dataset.intent_labels, ["intent1", "intent2"])
        self.assertEqual(dataset.intent_to_idx, {"intent1": 0, "intent2": 1})

    def test_use_embedding(self):
        """Test with use_embedding=True."""
        dataset = IntentDataset("test_corpus.json", use_embedding=True)
        self.assertIsInstance(dataset, Dataset)

    def test_prebuilt_vocab(self):
        """Test with a prebuilt vocabulary."""
        vocab = {
            "example": 1,
            "for": 2,
            "intent1": 3,
            "another": 4,
            "intent2": 5,
            "<UNK>": 0,
            "<PAD>": 6,
        }
        dataset = IntentDataset("test_corpus.json", prebuilt_vocab=vocab)
        self.assertEqual(dataset.word_to_idx, vocab)

    def test_custom_tokenizer(self):
        """Test using a custom tokenizer."""

        def custom_tokenizer(text):
            return text.split()

        dataset = IntentDataset("test_corpus.json", tokenizer=custom_tokenizer)
        self.assertEqual(dataset.tokenizer("test string"), ["test", "string"])

    def test_custom_vectorizer(self):
        """Test using a custom vectorizer."""

        def custom_vectorizer(tokens, vocab, max_length):
            return [vocab.get(token, vocab["<UNK>"]) for token in tokens] + [0] * (
                max_length - len(tokens)
            )

        dataset = IntentDataset("test_corpus.json", vectorizer=custom_vectorizer)
        tokens = tokenize("example for intent1")
        vector = dataset.vectorizer(tokens, dataset.word_to_idx, 20)
        self.assertEqual(vector[0], dataset.word_to_idx["example"])
        self.assertEqual(vector[1], dataset.word_to_idx["for"])
        self.assertEqual(vector[2], dataset.word_to_idx["intent1"])

    def test_invalid_index(self):
        """Test that an IndexError is raised for an invalid index."""
        dataset = IntentDataset("test_corpus.json")
        with self.assertRaises(IndexError):
            dataset[10]

    def test_data_types(self):
        """Test that the data types returned by __getitem__ are correct."""
        dataset = IntentDataset("test_corpus.json")
        sample, label = dataset[0]
        self.assertIsInstance(sample, torch.Tensor)
        self.assertIsInstance(label, torch.Tensor)
        self.assertEqual(label.dtype, torch.long)


if __name__ == "__main__":
    unittest.main()
