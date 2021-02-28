from loguru import logger

PERFORMANCE_METRICS = [
    "Accuracy",
    "Precision",
    "Recall",
    "F-measure",
]


def _compute_precision(performace):
    return float(performace["tp"]) / (performace["tp"] + performace["fp"])


def _compute_recall(performace):
    return float(performace["tp"]) / (performace["tp"] + performace["fn"])


def _compute_f_measure(precision, recall):
    return 2 * precision * recall / (precision + recall)


def _compute_accuracy(performace):
    return float((performace["tp"] + performace["tn"])) / float(
        (performace["tp"] + performace["tn"] + performace["fp"] + performace["fn"])
    )


def _compute_performance(performace, annotation, entities):
    prediction = [[ent.start_char, ent.end_char, ent.label_] for ent in entities]
    for entry in annotation + prediction:
        if entry in annotation and entry in prediction:
            performace["tp"] += 1
        elif entry in annotation and entry not in prediction:
            performace["fn"] += 1
        elif entry not in annotation and entry in prediction:
            performace["fp"] += 1
        else:
            performace["tn"] += 1


def show_performance(perform):
    logger.info("[+] Model Performances.")
    for metric in PERFORMANCE_METRICS:
        logger.info(" " * 4 + f"{metric}: {perform[metric]}")


def show_prediction(predict, description):
    logger.info("[+] Model Prediction:")
    for (start, end, label) in predict:
        logger.info(" " * 4 + f"[{label}] {description[start:end]}")


def test_model(model, testset):
    """ Test the trained model. """
    performance = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}

    for description, annotations in testset:
        doc = model(description)
        _compute_performance(performance, annotations["entities"], doc.ents)

    performance["Accuracy"] = _compute_accuracy(performance)
    performance["Precision"] = _compute_precision(performance)
    performance["Recall"] = _compute_recall(performance)
    performance["F-measure"] = _compute_f_measure(
        performance["Precision"], performance["Recall"]
    )
    return performance
