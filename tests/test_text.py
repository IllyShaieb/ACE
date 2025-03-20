"""test_text.py: Tests for the text module in the ACE program.

Ensures that the text processing functions work as expected.
"""

import unittest

import torch
import spacy

from brain.text import preprocessing

nlp = spacy.load("en_core_web_md")


class TestPreprocessing(unittest.TestCase):
    """Tests for the preprocessing module."""

    def test_tokenize(self):
        """Test the tokenize function with lowercase option."""
        test_cases = [
            ("Hello, world!", True, ["hello", ",", "world", "!"]),
            ("Hello, world!", False, ["Hello", ",", "world", "!"]),
            ("This is a test.", True, ["this", "is", "a", "test", "."]),
            ("This is a test.", False, ["This", "is", "a", "test", "."]),
            (
                "  leading and trailing spaces  ",
                True,
                ["leading", "and", "trailing", "spaces"],
            ),
            ("", True, []),
            ("123 456", True, ["123", "456"]),
            ("Hello! How are you?", True, ["hello", "!", "how", "are", "you", "?"]),
            ("this cost £100", True, ["this", "cost", "£", "100"]),
        ]

        for text, lowercase, expected_tokens in test_cases:
            with self.subTest(text=text, lowercase=lowercase):
                tokens = preprocessing.tokenize(text, lowercase=lowercase)
                self.assertEqual(tokens, expected_tokens)

    def test_build_vocab(self):
        """Test the build_vocab function."""
        test_cases = [
            (
                [["hello", "world"], ["another", "sentence", "!"]],
                {
                    "<PAD>": 0,
                    "<UNK>": 1,
                    "!": 2,
                    "another": 3,
                    "hello": 4,
                    "sentence": 5,
                    "world": 6,
                },
            ),
            (
                [["Hello", "world"], ["Another", "sentence", "!"]],
                {
                    "<PAD>": 0,
                    "<UNK>": 1,
                    "!": 2,
                    "Another": 3,
                    "Hello": 4,
                    "sentence": 5,
                    "world": 6,
                },
            ),
            (
                [[], []],
                {"<PAD>": 0, "<UNK>": 1},
            ),
            (
                [[]],
                {"<PAD>": 0, "<UNK>": 1},
            ),
            ([[""]], {"<PAD>": 0, "<UNK>": 1, "": 2}),
        ]

        for tokens, expected_vocab in test_cases:
            with self.subTest(tokens=tokens):
                vocab = preprocessing.build_vocab(tokens)
                self.assertEqual(vocab, expected_vocab)

    def test_vectorize(self):
        """Test the vectorize function."""
        vocab = {"<PAD>": 0, "<UNK>": 1, "hello": 2, "world": 3, "!": 4}
        test_cases = [
            (["hello", "world", "!"], 5, [2, 3, 4, 0, 0]),
            (["hello", "unknown", "world"], 3, [2, 1, 3]),
            ([], 3, [0, 0, 0]),
            (["unknown", "unknown"], 2, [1, 1]),
            (["hello", "world", "!", "extra"], 3, [2, 3, 4]),
            ([" ", ""], 2, [1, 1]),
        ]

        for tokens, max_length, expected_vector in test_cases:
            with self.subTest(tokens=tokens, max_length=max_length):
                vector = preprocessing.vectorize(tokens, vocab, max_length)
                self.assertEqual(vector, expected_vector)

    def test_build_embedding_vocab(self):
        """Test the build_embedding_vocab function."""
        tokenized_texts = [["hello", "world"], ["another", "sentence", "!"]]
        vocab = preprocessing.build_embedding_vocab(tokenized_texts)

        self.assertEqual(len(vocab), 5)  # 5 unique tokens
        self.assertTrue(all(isinstance(v, torch.Tensor) for v in vocab.values()))
        self.assertEqual(next(iter(vocab.values())).shape[0], nlp.vocab.vectors_length)

    def test_vectorize_embeddings(self):
        """Test the vectorize_embeddings function."""
        tokenized_texts = [["hello", "world"], ["another", "sentence", "!"]]
        vocab = preprocessing.build_embedding_vocab(tokenized_texts)
        max_length = 4
        token_list = ["hello", "world", "unknown", "sentence"]
        vectorized = preprocessing.vectorize_embeddings(token_list, vocab, max_length)

        self.assertIsInstance(vectorized, torch.Tensor)
        self.assertEqual(vectorized.shape, (max_length, nlp.vocab.vectors_length))
        self.assertTrue(
            torch.all(vectorized[2] == torch.zeros(nlp.vocab.vectors_length))
        )  # Test out of vocab vector.
        self.assertTrue(
            torch.all(vectorized[0] == vocab["hello"])
        )  # test in vocab vector.

    def test_vectorize_missing_tokens(self):
        """Test the vectorize function with missing tokens."""
        test_cases = [
            (
                {"<UNK>": 0},
                ValueError,
                "Raise exception when vocab does not contains <UNK>",
            ),
            (
                {"<PAD>": 0},
                ValueError,
                "Raise exception when vocab does not contains <PAD>",
            ),
        ]

        for vocab, error, reason in test_cases:
            with self.subTest(vocab=vocab, error=error, reason=reason):
                with self.assertRaises(error, msg=reason):
                    preprocessing.vectorize(["hello"], vocab)


if __name__ == "__main__":
    unittest.main()
