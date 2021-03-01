import re
import click
import json
from pathlib import Path
from rich.progress import track

URL_REGX_PATTERN = "https?://[^\s]+"
HASHTAG_REGEX_PATTERN = "#(\w+)"
MENTION_REGEX_PATTERN = "@(\w+)"
WHITESPACE_REGEX_PATTERN = " +"
HASH_MD5_REGEX_PATTERN = "([a-fA-F\d]{32})"


@click.group()
def preprocess():
    """ Generate and preprocess dataset. """
    pass


def _filter_no_reply_tweets(tweet_dataset):
    result = filter(lambda x: not x["reply_to"], tweet_dataset)
    result = filter(lambda x: not x["tweet"].startswith("@"), result)
    return list(result)


def _filter_only_english_tweets(tweet_dataset):
    result = filter(lambda x: x["language"] == "en", tweet_dataset)
    return list(result)


def _regex_match_https_url(text):
    urls = re.findall(URL_REGX_PATTERN, text)
    return urls


def _regex_match_hashtag(text):
    hashtags = re.findall(HASHTAG_REGEX_PATTERN, text)
    return hashtags


def _sanitize_text(text):
    # TODO(vancir): filter emoji.
    patterns = (
        URL_REGX_PATTERN,
        HASHTAG_REGEX_PATTERN,
        MENTION_REGEX_PATTERN,
        HASH_MD5_REGEX_PATTERN,
    )

    for pattern in patterns:
        text = re.sub(pattern, "", text)

    text = re.sub(WHITESPACE_REGEX_PATTERN, " ", text)
    text = text.strip()
    return text


def _unescape_symbol(text):
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&amp;", "&")
    text = text.replace("&apos;", "'")
    text = text.replace("&quot;", '"')
    return text


@preprocess.command()
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
def dataset(tweets, output):
    """Generate corpus.txt from raw tweets data."""

    tweets = Path(tweets)
    output = Path(output)

    with open(output, "a") as fout:
        for tweets_file in tweets.glob("*.json"):
            minimized_dataset = []
            with open(tweets_file) as f:
                for json_line in f.readlines():
                    tweet_json = json.loads(json_line)
                    minimized_dataset.append(tweet_json)

            minimized_dataset = _filter_only_english_tweets(minimized_dataset)
            minimized_dataset = _filter_no_reply_tweets(minimized_dataset)

            tweets_text = [
                _unescape_symbol(data["tweet"]) + "\n" for data in minimized_dataset
            ]
            fout.writelines(tweets_text)


@preprocess.command()
@click.option(
    "-c",
    "--corpus",
    help="the path of output corpus.txt.",
    type=click.Path(exists=True),
)
def tfidf(corpus):
    from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
    import numpy as np

    with open(corpus) as f:
        data = [_sanitize_text(line).strip() for line in f.readlines()]
        data = list(set(data))

    vectorizer = TfidfVectorizer(
        max_df=0.65,
        min_df=1,
        stop_words=ENGLISH_STOP_WORDS,
        use_idf=True,
        norm=None,
    )
    tfidf = vectorizer.fit_transform(data)
    features = vectorizer.get_feature_names()

    print("features:", len(features))
    with open("features.txt", "w") as f:
        for feature in features:
            f.write(feature + "\n")


@preprocess.command()
@click.option(
    "-c",
    "--corpus",
    help="the path of output corpus.txt.",
    type=click.Path(exists=True),
)
def textrank(corpus):
    from src.textrank import TextRank4Keyword

    with open(corpus) as f:
        data = [_sanitize_text(line).strip() for line in f.readlines()]
        data = list(set(data))

    features = set()
    for text in track(data):
        tr4w = TextRank4Keyword()
        tr4w.analyze(
            text,
            candidate_pos=["NOUN", "PROPN"],
            window_size=4,
            lower=False,
        )
        top_keywords = tr4w.get_keywords(10)
        top_keywords = dict(filter(lambda x: x[1] >= 1, top_keywords.items()))

        features |= set(top_keywords.keys())

    print("features:", len(features))
    with open("features.txt", "w") as f:
        for feature in features:
            f.write(feature + "\n")
