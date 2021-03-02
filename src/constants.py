import re
from src import settings

REGEX_URL = "https?://[^\s]+"
REGEX_HASHTAG = "#(\w+)"
REGEX_MENTION = "@(\w+)"
REGEX_WHITESPACE = " +"
REGEX_MD5 = "([a-fA-F\d]{32})"
REGEX_EMOJI_PATTERN = re.compile(
    pattern="["
    u"\U0001F600-\U0001F64F"  # emoticons
    u"\U0001F300-\U0001F5FF"  # symbols & pictographs
    u"\U0001F680-\U0001F6FF"  # transport & map symbols
    u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "]+",
    flags=re.UNICODE,
)

_SLANG_PATH = settings.get("data.SLANG")
with open(_SLANG_PATH) as f:
    _EXCLUSION_SLANG_WORDS = set(
        word.split(":", 1)[0].lower().replace("+", "\+") for word in f.readlines()
    )
    REGEX_SLANG = "|".join(_EXCLUSION_SLANG_WORDS)


RSSHUB_API = "https://rsshub.app/twitter/user/{user}"
