import spacy
from pathlib import Path
from loguru import logger

from src import utils
from src import settings
from src.ner import test
from src.ner import train
from src.ner import utils as train_utils


class Brain(object):
    def __init__(self, dataset="", ratio=0):
        ratio = ratio or settings.get("ner.DATA_SPLIT_RADIO")
        dataset = dataset or settings.get("ner.DATASET")
        self.dataset = train_utils.load_dataset(dataset)
        self.trainset, self.testset = train_utils.split_dataset(self.dataset, ratio)

        # setup later
        self.model = None
        self.performances = None

    def dump(self, name="", output=""):
        """ Dump NER model to local. """
        name = name or settings.get("ner.MODEL_NAME")
        output = Path(output or settings.get("ner.MODEL_PATH"))
        output.mkdir(exist_ok=True, parents=True)

        self.model.meta["name"] = name
        self.model.to_disk(output)
        logger.debug(f"Saved model to {output}")

    def dump_performance(self, output=""):
        output = Path(output or settings.get("ner.PERFORMANCE"))
        data = utils.load_json(output) if output.exists() else {}

        pd = {}
        for metric in test.PERFORMANCE_METRICS:
            pd[metric] = self.performances[metric]

        data[len(self.dataset)] = pd
        utils.dump_json(data, output)

    @classmethod
    def load(cls, model_path=""):
        """ Load NER model. """
        model_path = Path(model_path or settings.get("ner.MODEL_PATH"))
        if not model_path.exists():
            logger.error(f"Model path {model_path} not exists!")
            return None

        instance = cls()
        instance.model = spacy.load(model_path)
        return instance

    def train(self):
        self.model = train.train_model(self.trainset)

    def test(self):
        performances = test.test_model(self.model, self.testset)
        test.show_performance(performances)
        self.performances = performances

    def eval(self, description, show=True):
        doc = self.model(description)
        predictions = [[ent.start_char, ent.end_char, ent.label_] for ent in doc.ents]
        if show:
            test.show_prediction(predictions, description)
        return predictions
