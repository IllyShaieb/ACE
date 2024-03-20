"""
Collection of classes and functions for loading and manipulating data for the AI models.

#### Classes:

IntentClassifierDataset:
    All the data and functionality needed to train an intent classifier model.

#### Functions: None
"""
import random
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from ace.utils import Logger

logger = Logger.from_toml(config_file_name="logs.toml", log_name="data")


class IntentClassifierDataset:
    """
    All the data and functionality needed to train an intent classifier model.

    #### Parameters:

    file: Path
        The path to the file containing the data.

    shuffle: bool = False
        Whether or not to shuffle the data.

    seed: int (default: 42)
        The seed to use when shuffling the data.

    #### Methods:

    intents: list
        A list of all the intents in the dataset.

    split(train_percentage: float) -> tuple[pd.DataFrame, pd.DataFrame] (default: 0.8)
        Split the dataset into a training and test set.
    """

    def __init__(self, file: Path, shuffle: bool = False, seed: int = 42) -> None:
        self._seed = seed
        self.data = self._load_data(file, shuffle)

    def __len__(self) -> int:
        """
        The length of the dataset.

        #### Parameters: None

        #### Returns: int
            The length of the dataset.

        #### Raises: None
        """
        return len(self.data)

    def __getitem__(self, index: int) -> tuple[str, str]:
        """
        Get a tuple of the text and intent at the given index.

        #### Parameters:

        index: int
            The index of the data to get.

        #### Returns: tuple[str, str]
            A tuple of the text and intent at the given index.

        #### Raises: None
        """
        return tuple(self.data.iloc[index])

    @property
    def intents(self) -> list:
        """
        A list of all the intents in the dataset.
        """
        return self.data["intent"].unique().tolist()

    def split(self, train_percentage: float) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Split the dataset into a training and test set.

        #### Parameters:

        train_percentage: float
            The percentage of the dataset to use for training.

        #### Returns: tuple[pd.DataFrame, pd.DataFrame]
            A tuple of the training and test sets.

        #### Raises: None
        """

        with logger.log_context(
            "info",
            "Splitting dataset into training and test sets.",
            "Finished splitting dataset into training and test sets.",
        ):
            train = self.data.sample(frac=train_percentage, random_state=self._seed)
            test = self.data.drop(train.index)
            logger.log(
                "debug", f"Training length = {len(train)} :: Test Length {len(test)}"
            )
            return train, test

    def _load_data(self, file: Path, shuffle: bool) -> pd.DataFrame:
        """
        Helper function to load the data from the given file.

        #### Parameters:

        file: Path
            The path to the file containing the data.

        shuffle: bool
            Whether or not to shuffle the data.

        #### Returns: pd.DataFrame
            The data loaded from the given file.

        #### Raises: None
        """
        data = pd.read_csv(file)
        if shuffle:
            data = data.sample(frac=1, random_state=self._seed)
        return data


def load_entities(entities_directory: str = "data/rules/entities") -> dict:
    """
    Load the entities into a dictionary from the entities files.

    #### Parameters:

    entities_directory: str (default: "data/rules/entities")
        The directory containing the entity files.

    #### Returns: dict
        A dictionary of the entities and their values.

    #### Raises: FileNotFoundError
        If no entities are found in the given directory.
    """
    entities_dir = Path(entities_directory)

    with logger.log_context(
        "info",
        f"Loading raw entities dictionary from: {entities_dir}",
        "Finished creating raw entities",
    ):
        entities = {}
        for entity in entities_dir.glob("*.entity"):
            logger.log("debug", f"Loading entity: {entity}")

            content = entity.read_text().splitlines()

            if not content:
                logger.log("warning", f"Skipping empty entity file: {entity}")
                continue

            entities[entity.stem] = content

        # If entities is empty, then we have no entities
        if not entities:
            logger.log("fatal", "No entities found.")
            raise FileNotFoundError(
                f"No entities found in directory '{entities_dir}'."
            )

        return entities


def load_intents(intents_directory: str = "data/rules/intents") -> dict:
    """
    Load the intents into a dictionary from the intents files.

    #### Parameters:

    intents_directory: str (default: "data/rules/intents")
        The directory containing the intent files.

    #### Returns: dict
        A dictionary of the intents and their values.

    #### Raises: FileNotFoundError
        If no intents are found in the given directory.
    """
    intents_dir = Path(intents_directory)

    with logger.log_context(
        "info",
        f"Loading raw intents dictionary from: {intents_dir}",
        "Finished creating raw intents",
    ):
        intents = {
            intent.stem: intent.read_text().splitlines()
            for intent in intents_dir.glob("*.intent")
        }

        # If intents is empty, then we have no intents
        if not intents:
            logger.log("fatal", "No intents found.")
            raise FileNotFoundError(
                f"No intents found in directory '{intents_dir}'."
            )

    return intents


def generate_intent_dataset(
    raw_intents: dict, raw_entities: dict, attempts: int = 50, num_examples: int = 100
) -> tuple[dict, dict]:
    """
    Generates all combinations of intents and entities, but only if the entity is in the intent.

    #### Parameters:

    raw_intents: dict
        A dictionary of the intents and their values.

    raw_entities: dict
        A dictionary of the entities and their values.

    attempts: int (default: 50)
        The number of attempts to try before failing.

    num_examples: int (default: 100)
        The number of examples to generate for each intent.

    #### Returns: tuple[dict, dict]
        A tuple of the generated dataset and a dictionary of the
        number of fails for each intent.

        dict 1 - The generated dataset.
            format: {intent: [example1, example2, ...]}

        dict 2 - The number of fails for each intent.
            format: {intent: {"total": int, "entity": list, "duplicate": int}}

    #### Raises: None
    """

    dataset = {}
    fails = {}
    for intent, intent_template in tqdm(raw_intents.items(), desc="Creating dataset"):
        logger.log("info", f"Creating dataset for intent '{intent}'.")
        dataset[intent] = []

        fails[intent] = {"total": 0, "entity": [], "duplicate": 0}
        while len(dataset[intent]) < num_examples and fails[intent]["total"] < attempts:
            chosen_template = random.choice(intent_template).lower().split()
            logger.log("debug", f"Generating template number {len(dataset[intent])}.")

            for i, word in enumerate(chosen_template):
                if word.startswith("{") and word.endswith("}"):
                    entity = word[1:-1]

                    if entity in raw_entities:
                        chosen_entity = random.choice(raw_entities[entity])
                        chosen_template[i] = chosen_entity
                    else:
                        fails[intent]["entity"].append(entity)
                        continue

            chosen_template = " ".join(chosen_template).strip()

            # Add quote marks around the template if it contains a comma
            if "," in chosen_template:
                chosen_template = f'"{chosen_template}"'

            if chosen_template not in dataset[intent]:
                dataset[intent].append(chosen_template)
            else:
                fails[intent]["duplicate"] += 1

            fails[intent]["total"] = len(fails[intent]["entity"]) + fails[intent]["duplicate"]

    logger.log("debug", f"{dataset}")
    logger.log("debug", f"{fails}")

    return dataset, fails


def save_dataset(
    dataset: dict[str, list[str]], directory: str, filename: str = "dataset.csv"
) -> None:
    """
    Save the dataset to the given format.

    #### Parameters:

    dataset: dict[str, list[str]]
        The dataset to save.

    directory: str
        The directory to save the dataset to.

    filename: str (default: "dataset.csv")
        The name of the file to save the dataset to.

    #### Returns: None

    #### Raises: ValueError
        If the file type is not '.csv'.
    """
    root_dir = Path(directory)
    root_dir.mkdir(parents=True, exist_ok=True)

    save_path = root_dir / filename

    with logger.log_context(
        "info",
        f"Saving dataset to: {save_path}",
        "Finished saving dataset.",
    ):
        if save_path.suffix[1:].lower() != "csv":
            raise ValueError(
                f"Invalid file type '{save_path.suffix[1:]}' for dataset. Must be '.csv'."
            )
        with save_path.open("w") as f:
            f.write("phrase,intent\n")
            for intent, examples in dataset.items():
                for example in examples:
                    if "{" not in example:
                        f.write(f"{example},{intent}\n")
