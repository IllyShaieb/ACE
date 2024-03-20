from pathlib import Path

from ace.ai import data
import pytest


class TestIntentClassifierDataset:
    @pytest.fixture
    def dataset(self) -> data.IntentClassifierDataset:
        return data.IntentClassifierDataset(Path("data/intents/mock_intents.csv"))

    @pytest.fixture
    def dataset_with_shuffle(self) -> data.IntentClassifierDataset:
        return data.IntentClassifierDataset(
            Path("data/intents/mock_intents.csv"), shuffle=True
        )

    def test_intent_classifier_dataset_length(
        self, dataset, dataset_with_shuffle
    ) -> None:
        assert len(dataset) == 10
        assert len(dataset_with_shuffle) == 10

    def test_intent_classifier_dataset_intent_lengths(
        self, dataset, dataset_with_shuffle
    ) -> None:
        assert len(dataset.intents) == 3
        assert len(dataset_with_shuffle.intents) == 3

    def test_intent_classifier_dataset_get_item(self, dataset) -> None:
        assert dataset[0] == ("sentence 1", "example1")

    def test_intent_classifier_dataset_split(
        self, dataset, dataset_with_shuffle
    ) -> None:
        train, test = dataset.split(0.8)
        train_shuffled, test_shuffled = dataset_with_shuffle.split(0.8)

        assert len(train) == 8
        assert len(test) == 2

        assert len(train_shuffled) == 8
        assert len(test_shuffled) == 2


class TestLoadEntities:

    def test_load_entities(self) -> None:
        raw_entities = data.load_entities(entities_directory="tests/data/rules/entities")

        assert len(raw_entities) == 2

        for entity in raw_entities:
            assert entity in ["example_entity1", "example_entity2"]

    def test_load_entities_invalid_directory(self) -> None:
        with pytest.raises(FileNotFoundError):
            data.load_entities(entities_directory="tests/data/rules/invalid")

    def test_load_entities_empty_entity(self) -> None:
        raw_entities = data.load_entities(entities_directory="tests/data/rules/validations/empty")

        assert len(raw_entities) == 1


class TestLoadIntents:
    def test_load_intents(self) -> None:
        raw_intents = data.load_intents(intents_directory="tests/data/rules/intents")

        assert len(raw_intents) == 2

        for intent in raw_intents:
            assert intent in ["example1", "example2"]

    def test_load_intents_invalid_directory(self) -> None:
        with pytest.raises(FileNotFoundError):
            data.load_intents(intents_directory="tests/data/rules/invalid")


class TestGenerateIntentDataset:
    @pytest.fixture
    def mock_entities(self) -> dict[str, list[str]]:
        return {"example_entity1": ["entity1", "example1", "eg.1"], 
                "example_entity2": ["entity2", "example2", "eg.2"],
                "example_entity3": ["entity3", "example3", "eg.3"]}

    @pytest.fixture
    def mock_intents(self) -> dict[str, list[str]]:
        return {"intent1": ["Using {example_entity1}", "Another for {example_entity2}"],
                "intent2": ["Using {example_entity3}", "Another for {example_entity3}",
                            "And another for {example_entity3}"],
                "intent3": ["Using {example_entity1} and {example_entity2}", 
                            "Another for {example_entity1} and {example_entity2}",
                            "And another for {example_entity1} and {example_entity2}"]}

    @pytest.mark.skip(reason="Need to fix the issue with the test cases.")
    @pytest.mark.parametrize(
        "attempts, num_examples, dataset_length",
        [
            (1, 1, 1),
            (1, 2, 2),
            (2, 1, 1),
            (2, 2, 2),
            (3, 1, 1),
            (3, 2, 2),
            (3, 3, 3),
        ],
    )
    def test_generate_intent_dataset(self, attempts, num_examples, dataset_length, mock_entities, mock_intents) -> None:

        dataset, fails = data.generate_intent_dataset(
            raw_entities=mock_entities, raw_intents=mock_intents, attempts=attempts, num_examples=num_examples
        )

        assert all(len(dataset[intent]) == dataset_length for intent in dataset)
        assert all(fails[intent]["total"] >= 0 for intent in fails)


class TestSaveDataset:
    def test_save_dataset(self) -> None:
        dataset = {
            "intent1": ["example1", "example2"],
            "intent2": ["example3", "example4"],
        }

        save_dir = "tests/data/datasets"
        save_filename = "test_dataset.csv"

        data.save_dataset(dataset=dataset, directory=save_dir, filename=save_filename)

        assert Path(f"{save_dir}/{save_filename}").exists()

        Path(f"{save_dir}/{save_filename}").unlink()
        Path(f"{save_dir}").rmdir()

    def test_invalid_file_type(self) -> None:
        dataset = {
            "intent1": ["example1", "example2"],
            "intent2": ["example3", "example4"],
        }

        save_dir = "tests/data/datasets"
        save_filename = "test_dataset.txt"

        with pytest.raises(ValueError):
            data.save_dataset(dataset=dataset, directory=save_dir, filename=save_filename)

        assert not Path(f"{save_dir}/{save_filename}").exists()
