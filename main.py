r"""
########################################################################################
#                              ___       ______  _______                               #
#                             /   \     /      ||   ____|                              #
#                            /  ^  \   |  ,----'|  |__                                 #
#                           /  /_\  \  |  |     |   __|                                #
#                          /  _____  \ |  `----.|  |____                               #
#                         /__/     \__\ \______||_______|                              #
#                                                                                      #
#                                                                                      #
#    Welcome to ACE, the Artificial Consciousness Engine!                              #
#                                                                                      #
#    ACE is a digital assistant, designed to help you with your daily tasks and keep   #
#    you in the loop with your life and the world.                                     #
#                                                                                      #
########################################################################################
"""

import warnings

from ace.utils import Logger

warnings.filterwarnings("ignore")

logger = Logger.from_toml(config_file_name="logs.toml", log_name="main")

with logger.log_context(
    "info",
    "Importing modules in 'ace.py'",
    "Finished importing modules.",
):
    import typer

    from ace.interfaces import CLI, GUI

main_app = typer.Typer()
datasets_app = typer.Typer()
main_app.add_typer(datasets_app, name="datasets", help="Build and interact with datasets.")


@main_app.command()
def cli(
    no_header: bool = typer.Option(
        False,
        "--no-header",
        "-nh",
        help="Don't show the header.",
        show_default=True,
    ),
) -> None:
    """
    Run the ACE program, using the command line interface.
    """
    interface = CLI(show_header=not no_header, header=__doc__)
    logger.log("info", "Starting ACE.")
    interface.run()


@main_app.command()
def gui(
    no_header: bool = typer.Option(
        False,
        "--no-header",
        "-nh",
        help="Don't show the header.",
        show_default=True,
    ),
) -> None:
    """
    Run the ACE program, using the graphical user interface.
    """
    header = "\n\n".join(
        [
            "Welcome to ACE, the Artificial Consciousness Engine!",
            "ACE is a digital assistant, designed to help you with your daily tasks and keep you in the loop with your life and the world.",
        ]
    )

    interface = GUI(show_header=not no_header, header=header)
    logger.log("info", "Starting ACE.")
    interface.run()


@main_app.command()
def pipeline(
    no_train: bool = typer.Option(
        False,
        "--no-train",
        "-nt",
        help="Don't run training before testing.",
        show_default=True,
    ),
    no_test: bool = typer.Option(
        False,
        "--no-test",
        "-ns",
        help="Don't run testing after training.",
        show_default=True,
    ),
) -> None:
    """
    Train and test the AI models.
    """
    logger.log("info", "Starting the AI pipeline.")
    from ace.ai import models

    models_available = {
        "intent_classifier": models.IntentClassifierModel,
    }

    # Show a menu of the available models and let the user choose one.
    typer.echo("Available models:")
    for i, model in enumerate(models_available):
        typer.echo(f"{i + 1}. {model}")
    typer.echo()

    logger.log("info", f"Available models: {models_available}")

    # Create a model object based on the user's choice.
    model_choice = typer.prompt("Choose a model", type=int) - 1
    while model_choice not in range(len(models_available)):
        typer.echo("Invalid choice.")
        model_choice = typer.prompt("Choose a model", type=int) - 1
    model_name = list(models_available.keys())[model_choice]

    logger.log("info", f"Chosen model: {model_name}")

    config = models.IntentClassifierModelConfig.from_toml("config/ai.toml")

    # Train the model.
    if not no_train:
        typer.echo("===================== Training the model =====================")
        config.mode = "train"

        model = models_available[model_name](config)
        model.train()

    # Test the model.
    if not no_test:
        config.mode = "test"
        model = models_available[model_name](config)

        typer.echo("===================== Testing the model =====================")
        typer.echo("Type 'q' to quit.")
        while True:
            query = typer.prompt("Enter a query")
            logger.log("info", f"Query: {query}")

            if query == "q":
                break

            result = model.predict(query)
            logger.log("info", f"Intent: {result}")

            typer.echo(f"Intent: {result}")


@main_app.command()
def datasets() -> None:
    """
    Interact with the datasets.
    """


@datasets_app.command()
def intents(
    num_examples: int = typer.Option(
        20,
        "--examples",
        "-e",
        help="The number of examples to keep for each intent.",
        show_default=True,
    ),
    attempts: int = typer.Option(
        50,
        "--attempts",
        "-a",
        help="The number of attempts to generate an example.",
        show_default=True,
    ),
    rand_seed: int = typer.Option(
        None,
        "--seed",
        "-s",
        help="The random seed to use when sampling examples.",
        show_default=True,
    ),
    save_dir: str = typer.Option(
        "data/datasets",
        "--save-dir",
        "-d",
        help="The directory to save the dataset to.",
        show_default=True,
    ),
) -> None:
    """
    Interact with the intents dataset.

    You can generate a new dataset, visualise the dataset, and save the dataset.
    """
    logger.log("info", "Interacting with the intents dataset.")

    import random
    from pprint import pprint
    from datetime import datetime

    from ace.ai.data import (
        generate_intent_dataset,
        load_entities,
        load_intents,
        save_dataset,
    )

    random.seed = rand_seed
    logger.log("info", f"Random seed: {rand_seed}")

    typer.echo("============= Intents Dataset =============")

    dataset, fails = generate_intent_dataset(
        load_intents(), load_entities(), num_examples=num_examples, attempts=attempts
    )

    typer.echo(f"Random seed: {random.seed}")
    total_fails = sum(fails[intent]["total"] for intent in fails)
    typer.echo(f"Failed to generate {total_fails} examples:")
    for intent in fails:
        typer.echo(f"    {intent}: {fails[intent]['total']}")
        for fail in fails[intent]["entity"]:
            typer.echo(f"        {fail}")

    typer.echo()

    if typer.confirm("Visualise the dataset?"):
        typer.echo("Visualising the dataset...")
        logger.log("info", "Visualising the dataset.")

        pprint(dataset)
        typer.echo()

    if typer.confirm("Save the dataset?"):
        suffix = datetime.now().strftime("%Y%m%d")
        file_name = f"UK_EN_PA_Intents_{suffix}.csv"
        save_dataset(dataset, directory=save_dir, filename=file_name)
        typer.echo(f"Saved the dataset to '{save_dir}/{file_name}'")


if __name__ == "__main__":
    main_app()
