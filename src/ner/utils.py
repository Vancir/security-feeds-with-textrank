import random
from pathlib import Path
from loguru import logger

from src import utils


def load_dataset(path):
    """ Load NER dataset then split into trainset and testset. """

    """ Check whether if path exists. """
    path = Path(path)
    if not path.exists():
        logger.error(f"Dataset {path} not exists!")
        return None

    """ Load dataset as json. """
    dataset = utils.load_json(path)

    return dataset


def split_dataset(dataset, split_ratio):
    """ Shuffle dataset. """
    random.shuffle(dataset)

    """ Split dataset into two parts. """
    split = int(len(dataset) * split_ratio)

    return dataset[:split], dataset[split:]
