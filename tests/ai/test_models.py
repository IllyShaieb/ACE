"""test_models.py: Contains the unit tests for the machine learning models in the ACE program.

This module ensures the models used by ACE process the input correctly and produce the expected output.
"""

import unittest

import torch

from brain.ai import models


class TestTextClassifier(unittest.TestCase):
    """Unit tests for the TextClassifier model."""

    def setUp(self):
        """Set up common test components, which is called before each test."""
        self.vocab_size = 100
        self.embedding_dim = 1000
        self.hidden_dim = 100
        self.num_classes = 3
        self.batch_size = 1
        self.sequence_length = 20
        self.dropout_rate = 0.0  # Disable dropout for testing

    def create_model(self, use_embeddings=False, bidirectional=False):
        """Helper method to create a TextClassifier instance with specified parameters.

        Args:
            use_embeddings (bool): Whether to use pre-trained embeddings.
            bidirectional (bool): Whether to use a bidirectional LSTM.

        Returns:
            TextClassifier: An instance of the TextClassifier model.
        """
        return models.TextClassifier(
            vocab_size=self.vocab_size,
            embedding_dim=self.embedding_dim,
            hidden_dim=self.hidden_dim,
            num_classes=self.num_classes,
            dropout_rate=self.dropout_rate,
            bidirectional=bidirectional,
            use_embeddings=use_embeddings,
        )

    def create_input_tensor(self, use_embeddings=False):
        """Helper method to create an input tensor for testing.

        Args:
            use_embeddings (bool): Whether to use pre-trained embeddings.
        """
        if use_embeddings:
            # Create a random tensor of pre-trained embeddings.
            return torch.randn(
                self.batch_size, self.sequence_length, self.embedding_dim
            )
        else:
            # Create a random tensor of word indices.
            return torch.randint(
                0, self.vocab_size, (self.batch_size, self.sequence_length)
            )

    def test_forward_pass(self):
        """Test the forward pass of the TextClassifier model."""
        test_cases = [
            {"use_embeddings": False, "bidirectional": False},
            {"use_embeddings": True, "bidirectional": False},
            {"use_embeddings": False, "bidirectional": True},
            {"use_embeddings": True, "bidirectional": True},
        ]

        # Iterate through different configurations of use_embeddings and bidirectional
        for case in test_cases:
            model = self.create_model(
                use_embeddings=case["use_embeddings"],
                bidirectional=case["bidirectional"],
            )
            input_tensor = self.create_input_tensor(
                use_embeddings=case["use_embeddings"]
            )
            lengths = torch.randint(1, self.sequence_length, (self.batch_size,))
            output = model(input_tensor, lengths)

            self.assertEqual(
                output.shape,
                (self.batch_size, self.num_classes),
                "Forward pass output shape is incorrect.",
            )
            self.assertTrue(
                torch.all(output <= 0),
                "Output of LogSoftmax should be non-positive.",
            )  # Check that it is log softmax

    def test_variable_sequence_lengths(self):
        """Test the model with variable sequence lengths."""
        model = self.create_model()
        input_tensor = self.create_input_tensor(use_embeddings=False)
        lengths = torch.tensor([self.sequence_length - 5])  # Shorter sequence
        output = model(input_tensor, lengths)

        self.assertEqual(
            output.shape,
            (self.batch_size, self.num_classes),
            "Forward pass output shape is incorrect (variable sequence length).",
        )
        self.assertTrue(
            torch.all(output <= 0),
            "Output of LogSoftmax should be non-positive (variable sequence length).",
        )

    def test_batch_size_greater_than_one(self):
        """Test the model with a batch size greater than one."""
        batch_size = 4
        model = self.create_model()
        input_tensor = torch.randint(
            0, self.vocab_size, (batch_size, self.sequence_length)
        )
        lengths = torch.tensor([self.sequence_length] * batch_size)
        output = model(input_tensor, lengths)

        self.assertEqual(
            output.shape,
            (batch_size, self.num_classes),
            "Forward pass output shape is incorrect (batch size > 1).",
        )
        self.assertTrue(
            torch.all(output <= 0),
            "Output of LogSoftmax should be non-positive (batch size > 1).",
        )

    def test_zero_length_input(self):
        """Test the model with a zero-length input sequence."""
        model = self.create_model()
        input_tensor = self.create_input_tensor(use_embeddings=False)
        lengths = torch.tensor([0])  # Zero length sequence
        output = model(input_tensor, lengths)

        self.assertEqual(
            output.shape,
            (self.batch_size, self.num_classes),
            "Forward pass output shape is incorrect (zero-length input).",
        )
        self.assertTrue(
            torch.all(output <= 0),
            "Output of LogSoftmax should be non-positive (zero-length input)",
        )


if __name__ == "__main__":
    unittest.main()
