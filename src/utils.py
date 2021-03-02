import re
import json
import string

from src import constants


def load_json(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        obj = json.load(f)
    return obj


def load_json_lines(json_file):
    json_objs = []
    with open(json_file, "r", encoding="utf-8") as f:
        for json_line in f.readlines():
            obj = json.loads(json_line)
            json_objs.append(obj)
    return json_objs


def dump_json(obj, json_file, sort_keys=False):
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=sort_keys, ensure_ascii=False)


def is_ascii_word(word):
    return all(char in string.ascii_lowercase for char in word)


def sanitize_text(text):
    patterns = (
        constants.REGEX_URL,
        constants.REGEX_HASHTAG,
        constants.REGEX_MENTION,
        constants.REGEX_MD5,
    )

    for pattern in patterns:
        text = re.sub(pattern, "", text)

    text = constants.REGEX_EMOJI_PATTERN.sub(r"", text)
    text = re.sub(constants.REGEX_WHITESPACE, " ", text)
    return text.strip().lower()


def escape_quotes(text):
    return text.replace('"', '""')


def unescape_xml_symbol(text):
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&amp;", "&")
    text = text.replace("&apos;", "'")
    text = text.replace("&quot;", '"')
    return text
