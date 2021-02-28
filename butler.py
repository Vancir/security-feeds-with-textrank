import click
import importlib
from loguru import logger


@click.group()
def butler():
    pass


_butler_commands = (
    "annotator",
    "recognize",
    "generate",
    "preprocess",
)


def _setup_logger():
    logger.add("logs/{time}.log", level="DEBUG", rotation="10 MB")


def _setup_commands_for_butler():
    for cmd in _butler_commands:
        module = importlib.import_module(f"cli.{cmd}")
        method = getattr(module, cmd)
        butler.add_command(method)


if __name__ == "__main__":
    _setup_logger()
    _setup_commands_for_butler()
    butler()
