import sqlite3
from src import settings

_FEED_TABLE_SCHEMA = """
Tweets (
author      varchar(64),
title       varchar(512),
link        varchar(512),
published   varchar(64),
summary     varchar(512)
)
"""


class FeedStore(object):
    table = settings.get("sqlite.FEED_TABLE_NAME")
    database = settings.get("sqlite.LOCAL_SQLITE_DB")

    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    def __del__(self):
        self.conn.commit()
        self.conn.close()


def create_table():
    sql = f"create table if not exists {_FEED_TABLE_SCHEMA}"
    FeedStore.cursor.execute(sql)
    FeedStore.conn.commit()


def insert_feed(feed):
    # insert row to sqlite db
    columns = ", ".join(f'"{col}"' for col in feed.keys())
    values = ", ".join(f'"{val}"' for val in feed.values())
    data = '"{TABLE}" ({COLUMN}) values ({VALUE})'.format(
        TABLE=FeedStore.table, COLUMN=columns, VALUE=values
    )

    sql = f"insert into {data}"
    FeedStore.cursor.execute(sql)
    FeedStore.conn.commit()


def check_exists(feed):
    # check row exists in sqlite db
    sql = 'select exists(select 1 from {TABLE} where title="{TITLE}")'.format(
        TABLE=FeedStore.table, TITLE=feed["title"].replace('"', '""')
    )

    FeedStore.cursor.execute(sql)
    FeedStore.conn.commit()
    return True if FeedStore.cursor.fetchone()[0] else False
