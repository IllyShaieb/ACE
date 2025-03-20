"""models.py: Contains the machine learning models for the ACE program.

This module provides the machine learning models used in the ACE program,
including models for intent classification.
"""

import torch
import torch.nn as nn
import torch.nn.utils.rnn as rnn_utils


class TextClassifier(nn.Module):
    """A text classification model with LSTM and dropout.

    This model is designed for text classification tasks, such as intent
    recognition. It uses an LSTM (Long Short-Term Memory) network to process
    sequential data and includes dropout for regularization.
    """

    def __init__(
        self,
        vocab_size: int,
        embedding_dim: int,
        hidden_dim: int,
        num_classes: int,
        dropout_rate: float = 0.5,
        bidirectional: bool = False,
        use_embeddings: bool = False,
    ):
        """Initializes the TextClassifier.

        Args:
            vocab_size: The number of unique words in the vocabulary.
                        This determines the size of the embedding layer.
            embedding_dim: The dimension of the word embeddings.  This is the size of
                            the vectors that represent each word.
            hidden_dim: The dimension of the hidden state in the LSTM. This controls
                        the amount of information the LSTM can retain.
            num_classes: The number of classes for classification.  This is the number of
                        possible intents or categories.
            dropout_rate: The dropout rate for regularization. Dropout helps prevent
                            overfitting by randomly setting a fraction of neuron activations
                            to zero during training.
            bidirectional: Whether to use a bidirectional LSTM. A bidirectional LSTM
                            processes the input sequence in both directions, allowing it to
                            capture information from both past and future context.
            use_embeddings: Whether to use word embeddings. If using vector embeddings,
                            the embedding layer is not needed.
        """
        super(TextClassifier, self).__init__()

        # Store the parameters
        self.use_embeddings = use_embeddings
        self.num_classes = num_classes

        # If not using pre-trained embeddings, create an embedding layer.
        # This layer converts word indices into dense vector representations.
        if not use_embeddings:
            self.embedding = nn.Embedding(vocab_size, embedding_dim)

        # Define the LSTM layer.
        # It takes the embedding dimension as input and outputs a hidden state
        # of size hidden_dim.
        self.lstm = nn.LSTM(
            embedding_dim,
            hidden_dim,
            batch_first=True,  # The input and output tensors are provided as (batch, seq, feature)
            bidirectional=bidirectional,
        )

        # Define the dropout layer
        self.dropout = nn.Dropout(dropout_rate)

        # Define the linear layer that maps the LSTM output to the number of classes.
        # The input size depends on whether the LSTM is bidirectional.
        self.linear = nn.Linear(
            hidden_dim * 2 if bidirectional else hidden_dim, num_classes
        )

        # Define the LogSoftmax layer.  This layer outputs log probabilities, which are
        # useful for numerical stability and are expected by some loss functions like
        # nn.CrossEntropyLoss.
        self.softmax = nn.LogSoftmax(dim=1)

    def forward(self, x: torch.Tensor, lengths: torch.Tensor) -> torch.Tensor:
        """Forward pass of the model.

        Args:
            x: The input tensor.
            lengths: The lengths of the sequences in the batch.

        Returns:
            The output tensor, which is the log probabilities of the classes.
        """

        # If not using pre-trained embeddings, pass the input through the embedding layer.
        if not self.use_embeddings:
            x = self.embedding(x)

        # Handle the case where a sequence has zero length.
        if torch.any(lengths == 0):
            # If any sequence length is zero, return a zero tensor of the appropriate shape.
            batch_size = x.size(0)
            return torch.zeros(
                (batch_size, self.num_classes), dtype=x.dtype, device=x.device
            )

        # Pack the padded sequence. This is an optimization technique that allows
        # the LSTM to process variable-length sequences more efficiently by
        # skipping the padding.
        packed_input = rnn_utils.pack_padded_sequence(
            x, lengths.cpu(), batch_first=True, enforce_sorted=False
        )

        # Pass the packed sequence through the LSTM layer.
        packed_output, _ = self.lstm(packed_input)

        # Unpack the padded sequence. This converts the packed sequence back to
        # a padded tensor.
        lstm_out, _ = rnn_utils.pad_packed_sequence(packed_output, batch_first=True)

        # Get the output of the LSTM at the last non-padding time step for each sequence.
        # This is the relevant output for classification.
        x = lstm_out[torch.arange(lstm_out.size(0)), lengths - 1]

        # Apply dropout for regularization
        x = self.dropout(x)

        # Pass the output through the linear layer
        x = self.linear(x)

        return self.softmax(x)


if __name__ == "__main__":  # pragma: no cover
    models = [
        TextClassifier(
            vocab_size=100,
            embedding_dim=1000,
            hidden_dim=100,
            num_classes=3,
            dropout_rate=0.5,
            bidirectional=True,
            use_embeddings=False,
        ),
    ]

    print(" Available Models ".center(80, "="))
    for model in models:
        print(model)
        print()

        # Pass an example tensor through the model and show the output
        example_tensor = torch.randint(0, 100, (1, 20))
        output = model(example_tensor, torch.tensor([20]))
        print(f"Example tensor: {example_tensor.shape} | {example_tensor}")
        print(f"Output: {output.shape} | {output}")
        print(f"Output Probabilities: {torch.exp(output)}")
        print(f"Prediction: {torch.argmax(output, dim=1)}")

        print("-" * 80)
        print()
