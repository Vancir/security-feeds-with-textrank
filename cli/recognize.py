import click

from src import settings
from src.ner.analyzer import Brain

DEFAULT_MODEL_PATH = settings.get("ner.MODEL_PATH")


@click.command()
@click.argument("text")
@click.option(
    "-m",
    "--model",
    default=DEFAULT_MODEL_PATH,
    type=click.Path(exists=True),
    help="path of trained nlp model.",
)
def recognize(text, model):
    """ Recognize label within text using trained NER model. """
    if model.exists():
        brain = Brain.load(model)
    else:
        brain = Brain()
        brain.train()
        brain.test()
        brain.dump()

    brain.eval(text)
