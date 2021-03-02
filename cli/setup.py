import click
from pathlib import Path
from rich.progress import track

from src import utils
from src import database
from src.textrank import TextRank


@click.group()
def setup():
    """ Generate and preprocess dataset. """
    pass


def _filter_no_reply_tweets(tweet_dataset):
    result = filter(lambda x: not x["reply_to"], tweet_dataset)
    result = filter(lambda x: not x["tweet"].startswith("@"), result)
    return list(result)


def _filter_only_english_tweets(tweet_dataset):
    result = filter(lambda x: x["language"] == "en", tweet_dataset)
    return list(result)


@setup.command()
@click.option(
    "-t",
    "--tweets",
    help="the path of exported tweets file.",
    type=click.Path(exists=True),
)
@click.option(
    "-o",
    "--output",
    help="the path of output corpus.txt.",
    type=click.Path(),
)
def corpus(tweets, output):
    """Generate corpus.txt from raw tweets data."""

    tweets = Path(tweets)
    output = Path(output)
    output_clean = output.parent / (output.name + "_clean" + output.suffix)

    output = open(output, "a")
    output_clean = open(output_clean, "a")

    for tweets_file in tweets.glob("*.json"):
        minimized_dataset = utils.load_json_lines(tweets_file)
        minimized_dataset = _filter_only_english_tweets(minimized_dataset)
        minimized_dataset = _filter_no_reply_tweets(minimized_dataset)

        tweets_text = [
            utils.unescape_xml_symbol(data["tweet"]) + "\n"
            for data in minimized_dataset
        ]

        tweets_clean_text = [
            utils.sanitize_text(data["tweet"]) + "\n" for data in minimized_dataset
        ]

        output.writelines(tweets_text)
        output_clean.writelines(tweets_clean_text)

    output.close()
    output_clean.close()


@setup.command()
@click.option(
    "-c",
    "--clean-corpus",
    help="the path of corpus.txt.",
    type=click.Path(exists=True),
)
@click.option(
    "-o",
    "--output",
    help="the path of output features.txt.",
    default="assets/keywords.txt",
)
def keyword(clean_corpus, output):

    with open(clean_corpus) as f:
        data = [line for line in f.readlines()]
        data = list(set(data))

    keywords = set()
    textrank = TextRank()

    for text in track(data):
        textrank.analyze(
            text,
            candidate_pos=["NOUN", "PROPN"],
            window_size=4,
            lower=False,
        )
        top_keywords = textrank.get_keywords(10)
        top_keywords = textrank.filter_keywords(top_keywords)
        keywords |= set(top_keywords)

    print("keywords count:", len(keywords))

    with open(output, "w") as f:
        for keyword in keywords:
            f.write(keyword + "\n")


@setup.command()
def database():
    """Setup sqlite3 database."""
    database.create_table()
