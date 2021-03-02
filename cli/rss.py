import re
import click
from loguru import logger

import feedparser
from src import utils
from src import database
from src import constants
from src import settings
from src.textrank import TextRank


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
    for user in following_accounts:
        try:
            user_unread_feed = _get_user_feeds(user)
            unread_feeds += user_unread_feed
        except Exception as e:
            logger.exception(f"failed to get twitter {user} feed from rsshub.")
            return

    textrank = TextRank()
    for unread_feed in unread_feeds:
        text = unread_feed["summary"]
        textrank.analyze(
            text,
            candidate_pos=["NOUN", "PROPN"],
            window_size=4,
            lower=False,
        )
        keywords = textrank.get_keywords(10)
        keywords = textrank.filter_keywords(keywords)

        feed_report = [text, _get_text_entities(text, keywords)]
        reports.append(feed_report)

    utils.dump_json(reports, output)
