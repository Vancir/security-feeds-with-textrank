import spacy
import random
import warnings
from loguru import logger
from rich.progress import track
from spacy.util import minibatch, compounding

from src import settings

TRAIN_DROP_RATE = settings.get("ner.TRAIN_DROP_RATE")
TRAIN_ITER_TIMES = settings.get("ner.TRAIN_ITER_TIMES")

MODEL_LABELS = [
    "SOFTWARE",
    "VERSION",
    "TECHNOLOGY",
]


def _get_component(model):
    # create the built-in pipeline components and add them to the pipeline
    # nlp.create_pipe works for built-ins that are registered with spaCy
    if "ner" not in model.pipe_names:
        ner = model.create_pipe("ner")
        model.add_pipe(ner)
    else:
        # otherwise, get it so we can add labels
        ner = model.get_pipe("ner")
    return ner


def train_model(trainset):
    # create blank Language class
    model = spacy.blank("en")
    ner = _get_component(model)
    for label in MODEL_LABELS:
        ner.add_label(label)
    optimizer = model.begin_training()

    # get names of other pipes to disable them during training
    other_pipes = [pipe for pipe in model.pipe_names if pipe != "ner"]
    with model.disable_pipes(*other_pipes), warnings.catch_warnings():
        # show warnings for misaligned entity spans once
        warnings.filterwarnings("once", category=UserWarning, module="spacy")

        for _ in track(range(TRAIN_ITER_TIMES)):
            random.shuffle(trainset)
            losses = {}

            batches = minibatch(trainset, size=compounding(4.0, 32.0, 1.001))
            for batch in batches:
                texts, annotations = zip(*batch)
                model.update(
                    texts,  # batch of texts
                    annotations,  # batch of annotations
                    sgd=optimizer,
                    drop=TRAIN_DROP_RATE,  # dropout - make it harder to memorise data
                    losses=losses,
                )
    logger.debug("Finished training NER model.")
    return model
