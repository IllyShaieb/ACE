"""
Contains the logic for training various models and using them to make predictions.

#### Classes:

IntentClassifierModelConfig:
    Holds the configuration for the intent classifier model.

IntentClassifierModel:
    A model that can be used to classify intents.

NERModelConfig:
    Holds the configuration for the named entity recognition model.

NERModel:
    A model that can be used to recognize named entities.

#### Functions: None
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Union
from statistics import stdev, mean

import spacy
import toml
from spacy.tokens import DocBin
from tqdm import tqdm

from ace.ai import data
from ace.utils import Logger

SEED = 42
CONFIG_PATH = os.path.join("config", "ai.toml")

logger = Logger.from_toml(config_file_name="logs.toml", log_name="models")


@dataclass
class IntentClassifierModelConfig:
    """
    Holds the configuration for the intent classifier model.

    #### Parameters:

    spacy_model: str (default: "en")
        The name of the spaCy model to use.

    data_path: str (default: "data/intents/intents.csv")
        The path to the data file.

    train_percentage: float (default: 0.5)
        The percentage of the data to use for training.

    train_data_save_path: str (default: "data/intents/train.spacy")
        The path to save the training data to.

    valid_data_save_path: str (default: "data/intents/dev.spacy")
        The path to save the validation data to.

    rebuild_config: bool (default: False)
        Whether or not to rebuild the config file.

    rebuild_data: bool (default: False)
        Whether or not to rebuild the data files.

    best_model_location: str (default: "models/intents/model-best")
        The path to save the best model to.

    threshold: float (default: 0.5)
        The threshold to use when predicting the intent.

    base_config: str (default: "data/intents/base_config.cfg")
        The path to the base config file.

    output_dir: str (default: "models/intents")
        The path to save the model to.

    mode: str (default: "train")
        The mode to run the model in. Can be "train" or "predict".

    #### Methods:

    from_toml(config_file: Union[str, None] = None) -> IntentClassifierModelConfig
        Load the configuration from a TOML file. Leave the config_file parameter
        empty to load the configuration from the default location: config/ai.toml.
    """

    spacy_model: str = "en"
    data_path: str = "data/intents/intents.csv"
    train_percentage: float = 0.5
    train_data_save_path: str = "data/intents/train.spacy"
    valid_data_save_path: str = "data/intents/dev.spacy"
    rebuild_config: bool = False
    rebuild_data: bool = False
    best_model_location: str = "models/intents/model-best"
    threshold: float = 0.5
    base_config: str = "data/intents/base_config.cfg"
    output_dir: str = "models/intents"
    mode: str = "train"

    @staticmethod
    def from_toml(
        config_file: Union[str, None] = None
    ) -> "IntentClassifierModelConfig":
        """
        Load the configuration from a TOML file. Leave the config_file parameter
        empty to load the configuration from the default location: config/ai.toml.

        #### Parameters:

        config_file: Union[str, None] (default: None)
            The path to the TOML file to load the configuration from.

        #### Returns: IntentClassifierModelConfig
            The configuration object for the intent classifier model.

        #### Raises: None
        """
        config = toml.load(config_file or CONFIG_PATH)
        return IntentClassifierModelConfig(**config["IntentClassifierModelConfig"])


@dataclass
class NERModelConfig:
    """
    Holds the configuration for the named entity recognition model.

    #### Parameters:

    spacy_model: str (default: "en_core_web_md")
        The name of the spaCy model to use.

    #### Methods:

    from_toml(config_file: Union[str, None] = None) -> NERModelConfig
        Load the configuration from a TOML file. Leave the config_file parameter
        empty to load the configuration from the default location: config/ai.toml.
    """

    spacy_model: str = "en_core_web_md"

    @staticmethod
    def from_toml(config_file: Union[str, None] = None) -> "NERModelConfig":
        """
        Load the configuration from a TOML file. Leave the config_file parameter
        empty to load the configuration from the default location: config/ai.toml.

        #### Parameters:

        config_file: Union[str, None] (default: None)
            The path to the TOML file to load the configuration from.

        #### Returns: NERModelConfig
            The configuration object for the named entity recognition model.

        #### Raises: None
        """
        config = toml.load(config_file or CONFIG_PATH)
        return NERModelConfig(**config["NERModelConfig"])


class IntentClassifierModel:
    """
    Contains the logic for training and predicting the intent of a given text.

    #### Parameters:

    config: IntentClassifierModelConfig (default: IntentClassifierModelConfig())
        The configuration object for the intent classifier model.

    #### Methods:

    predict(text: str) -> str
        Predict the intent of the given text.

    train() -> None
        Prepares the data and trains the model using the given configuration.
    """

    def __init__(
        self, config: IntentClassifierModelConfig = IntentClassifierModelConfig()
    ) -> None:
        self.config = config
        self.nlp = self._load_spacy_model(self.config.spacy_model)

    def predict(self, text: str) -> str:
        """
        Predict the intent of the given text.

        #### Parameters:

        text: str
            The text to predict the intent of.

        #### Returns: str
            The predicted intent.

        #### Raises: None
        """
        doc = self.nlp(text.strip().lower() if text else "")

        try:
            prediction = max(doc.cats, key=doc.cats.get)  # type: ignore
        except ValueError:
            logger.log("error", "No predictions found")
            return "unknown"

        return (
            "unknown"
            if self._confidence(doc.cats) < self.config.threshold
            else prediction
        )

    def train(self) -> None:  # pragma: no cover
        """
        Prepares the data and trains the model using the given configuration.

        #### Parameters: None

        #### Returns: None

        #### Raises: None
        """
        if self.config.rebuild_data:
            logger.log("debug", f"Preparing data using: {self.config}")
            self._prepare_data()

        base_config = Path(self.config.base_config)
        full_config = base_config.with_name("config.cfg")

        if self.config.rebuild_config:
            with logger.log_context(
                "debug", "Building spaCy config", "spaCy config built"
            ):
                os.system(
                    f"poetry run python -m spacy init fill-config {base_config} {full_config}"
                )

        with logger.log_context(
            "debug",
            f"Training {type(self).__name__} using spaCy",
            f"{type(self).__name__} trained using spaCy",
        ):
            os.system(
                f"poetry run python -m spacy train {full_config} --output {Path(self.config.output_dir)}"
            )

    def _load_spacy_model(
        self, spacy_model: str = "en"
    ) -> spacy.language.Language:  # pragma: no cover
        """
        Helper function to load the correct spaCy language model.

        #### Parameters:

        spacy_model: str (default: "en")
            The name of the spaCy model to load.

        #### Returns: spacy.language.Language
            The spaCy language model.

        #### Raises: None
        """
        if self.config.mode == "train":
            return (
                spacy.blank(spacy_model)
                if spacy_model == "en"
                else spacy.load(spacy_model)
            )
        return spacy.load(self.config.best_model_location)

    def _make_spacy_docs(
        self,
        data: list[tuple[str, str]],
        for_training: bool = True,
    ) -> list:  # pragma: no cover
        """
        Helper function to create take a list of texts and labels and
        create a list of spaCy docs.

        #### Parameters:

        data: list[tuple[str, str]]
            A list of tuples containing the text and the label.

        for_training: bool (default: True)
            Whether the docs are being created for training or validation.

        #### Returns: list
            A list of spaCy docs.

        #### Raises: None
        """
        docs = []
        for doc, label in tqdm(
            self.nlp.pipe(data, as_tuples=True),
            total=len(data),
            desc="Creating train docs" if for_training else "Creating valid docs",
        ):
            doc.cats[label] = 1
            docs.append(doc)

        return docs

    def _prepare_data(self) -> None:  # pragma: no cover
        """
        Helper function to prepare and save the data for training and validation.

        #### Parameters: None

        #### Returns: None

        #### Raises: None
        """
        dataset = data.IntentClassifierDataset(
            Path(self.config.data_path), shuffle=True
        )
        train_data, test_data = dataset.split(self.config.train_percentage)

        train_docs = self._make_spacy_docs(train_data.values.tolist())
        test_docs = self._make_spacy_docs(test_data.values.tolist(), False)

        train_bin = DocBin(docs=train_docs)
        test_bin = DocBin(docs=test_docs)

        train_bin.to_disk(self.config.train_data_save_path)
        test_bin.to_disk(self.config.valid_data_save_path)

    def _confidence(self, predictions: dict) -> float:  # pragma: no cover
        """
        Helper function to calculate the confidence of the model's prediction.
        This is done by getting the standard deviation of the prediction and
        dividing it by the mean of the predictions.

        #### Parameters:

        predictions: dict
            A dictionary containing the predictions of the model.

        #### Returns: float
            The confidence of the model's prediction.

        #### Raises: None
        """
        sorted_predictions = sorted(
            predictions.items(), key=lambda x: x[1], reverse=True
        )
        logger.log("debug", f"Predictions: {sorted_predictions}")
        if all(x[1] == 0 for x in sorted_predictions):
            return 0
        return stdev([x[1] for x in sorted_predictions]) / mean(
            [x[1] for x in sorted_predictions]
        )


class NERModel:
    """
    Contains the logic for the named entity recognition model.

    #### Parameters:

    config: NERModelConfig (default: NERModelConfig())
        The configuration for the model.

    #### Methods:

    predict(text: str) -> list[tuple[str, str]]
        Predict the named entities of the given text.
    """

    def __init__(self, config: NERModelConfig = NERModelConfig()) -> None:
        self.config = config
        self.nlp = self._load_spacy_model(self.config.spacy_model)

    def predict(self, text: str) -> list[tuple[str, str]]:
        """
        Predict the named entities of the given text.

        #### Parameters:

        text: str
            The text to predict the named entities of.

        #### Returns: list[tuple[str, str]]
            A list of tuples containing the named entity and its label.

        #### Raises: None
        """
        doc = self.nlp(text.strip() if text else "")
        return [(ent.text, ent.label_) for ent in doc.ents]

    def _load_spacy_model(
        self, spacy_model: str = "en"
    ) -> spacy.language.Language:  # pragma: no cover
        """
        Helper function to load the correct spaCy language model.

        #### Parameters:

        spacy_model: str (default: "en")
            The name of the spaCy model to load.

        #### Returns: spacy.language.Language
            The spaCy language model.

        #### Raises: None
        """
        return (
            spacy.blank(spacy_model) if spacy_model == "en" else spacy.load(spacy_model)
        )
