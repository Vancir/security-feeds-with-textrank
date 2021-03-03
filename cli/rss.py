import re
import click
from loguru import logger
from bs4 import BeautifulSoup
from rich.progress import track

import feedparser
from src import utils
from src import database
from src import constants
from src import settings


@click.group()
def rss():
    """ RSS reader cli. """
    pass


def _construct_feed(entry):
    return {
        "title": utils.escape_quotes(entry["title"]),
        "link": entry["link"],
        "summary": utils.escape_quotes(entry["summary"]),
        "published": entry["published"],
        "author": entry["author"],
    }


def _parse_and_store_entries(data):
    unread_feeds = []
    for entry in data["entries"]:
        # skip reply tweet.
        if entry["title"].startswith("Re"):
            continue

        feed = _construct_feed(entry)

        if not database.check_exists(feed):
            database.insert_feed(feed)
            unread_feeds.append(feed)

    return unread_feeds


def _get_user_feeds(user):
    api = constants.RSSHUB_API.format(user=user)
    data = feedparser.parse(api)
    unread_feeds = _parse_and_store_entries(data)
    return unread_feeds


def _get_text_entities(text, keywords):
    entities = []
    for keyword in keywords:
        for m in re.finditer(keyword, text):
            start = m.start()
            stop = start + len(keyword)
            label = "KEYWORD"
            entity = [start, stop, label]
            entities.append(entity)
    return {"entities": entities}


@rss.command()
@click.option(
    "-o",
    "--output",
    help="the path of output report.json.",
    default="assets/report.json",
)
def today(output):
    reports = []

    unread_feeds = []
    following_accounts = settings.get("subscribe")
    for user in track(following_accounts, description="Querying twitter..."):
        try:
            user_unread_feed = _get_user_feeds(user)
            unread_feeds += user_unread_feed
        except:
            logger.info(f"Failed to get {user} tweets.")

    logger.info(f"Get {len(unread_feeds)} unread feeds.")

    with open("assets/features.txt") as f:
        keywords = [word.strip() for word in f.readlines()]
        keywords = "|".join(keywords)
        keyword_pattern = re.compile(keywords)

    for unread_feed in unread_feeds:
        try:
            text = unread_feed["summary"]
            text = utils.unescape_quotes(text)
            soup = BeautifulSoup(text, "html.parser")
            text = soup.text
            if not text:
                continue

            matched_keywords = keyword_pattern.match(text)
            if not matched_keywords:
                continue
            feed_report = [text, _get_text_entities(text, matched_keywords)]
            reports.append(feed_report)
        except Exception as e:
            logger.exception(e)

    utils.dump_json(reports, output)
