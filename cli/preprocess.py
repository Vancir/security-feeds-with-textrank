import re
import click
import json

from pathlib import Path

URL_REGX_PATTERN = "https?://[^\s]+"
HASHTAG_REGEX_PATTERN = "#(\w+)"
WHITESPACE_REGEX_PATTERN = " +"


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
    patterns = (
        URL_REGX_PATTERN,
        HASHTAG_REGEX_PATTERN,
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
