import os
import re
import sys
import click
from readchar import readkey
from pathlib import Path

from src import utils


TERM_RED_COLOR = "\033[1;31m"
TERM_GREEN_COLOR = "\033[1;32m"
TERM_YELLOW_COLOR = "\033[1;33m"
TERM_BLUE_COLOR = "\033[1;34m"
TERM_PURPLE_COLOR = "\033[1;35m"
TERM_SYMBOL_COLOR = "\033[1;36m"
TERM_WHITE_COLOR = "\033[1;37m"
TERM_RESET_COLOR = "\033[0m"


def red(word):
    return TERM_RED_COLOR + word + TERM_RESET_COLOR


def green(word):
    return TERM_GREEN_COLOR + word + TERM_RESET_COLOR


def yellow(word):
    return TERM_YELLOW_COLOR + word + TERM_RESET_COLOR


def blue(word):
    return TERM_BLUE_COLOR + word + TERM_RESET_COLOR


def purple(word):
    return TERM_PURPLE_COLOR + word + TERM_RESET_COLOR


def symbol(word):
    return TERM_SYMBOL_COLOR + word + TERM_RESET_COLOR


def white(word):
    return TERM_WHITE_COLOR + word + TERM_RESET_COLOR


KEY_LEFT_ARROW = "\x1b[D"
KEY_RIGHT_ARROW = "\x1b[C"
KEY_UP_ARROW = "\x1b[A"
KEY_DOWN_ARROW = "\x1b[B"
KEY_ENTER = "\r"
KEY_SPACE = " "

LABELS = {"k": "KEYWORD"}

LABELS_COLOR = {
    "KEYWORD": red,
    "CURRENT": purple,
}


def print_colorful_description(desc, word_start, word_end, entities):
    """ Highlight current word. """

    tags = entities.copy()
    intags = [
        tag
        for tag in tags
        if (tag[0] <= word_start and word_end <= tag[1])  # word located at tag internal
        or (word_start < tag[0] <= word_end)  # word located at start_tag half part
        or (word_start < tag[1] <= word_end)  # word located at stop_tag half part
    ]

    if not intags:
        tags.append([word_start, word_end, "CURRENT"])
    tags = sorted(tags, key=lambda x: x[0])
    """ print colorful description. """
    i = 0
    output = ""
    for _start, _stop, _label in tags:
        output += "".join(
            [
                desc[i:_start],
                LABELS_COLOR[_label](desc[_start:_stop]),
            ]
        )
        i = _stop
    print("".join([output, desc[i:]]), flush=True)
    print()

    print_label()
    """ print prompt. """
    word = desc[word_start:word_end]
    print(
        "{} {}{}{}".format(symbol("️➡️️"), white("("), yellow(word), white(") = ")),
        end="",
    )
    """ flush to stdout. """
    sys.stdout.flush()


def print_label():
    print(
        symbol("️➡️"),
        white("(label) ="),
        "{}-{}".format(
            LABELS_COLOR["KEYWORD"]("k"),
            LABELS_COLOR["KEYWORD"]("KEYWORD"),
        ),
    )


def print_usage():
    print("\n\nhelp:")
    print(symbol("⬆️"), white("move forward one character."))
    print(symbol("⬇️️"), white("move backward one character."))
    print(symbol("⬅️"), white("move to previous word."))
    print(symbol("️➡️️"), white("move to next word."))
    print(symbol("u"), white("unset the current highlighted word."))
    print(symbol("q"), white("quit the annotator."))
    print(symbol("🔄"), white("go to the next paragraph."))

    _ = readkey()


def get_wordlists(desc):
    wordlists = []
    """ Get standlone word and strip some punctuation. """
    for m in re.finditer(r"\S+", desc):
        start, word = m.start(), m.group()

        # Remove end colon.
        while (
            word.endswith(",")
            or word.endswith(".")
            or word.endswith(":")
            or word.endswith(";")
            or word.endswith('"')
            or word.endswith("`")
            or word.endswith("'")
        ):
            word = word[:-1]

        while (
            word.startswith('"')
            or word.startswith("(")
            or word.startswith("`")
            or word.startswith("'")
        ):
            start += 1
            word = word[1:]

        stop = start + len(word)
        wordlists.append([start, stop, word])
    return wordlists


def user_control(desc, entities=[]):
    """ wordlists: Store result extracted by regex. """
    wordlists = get_wordlists(desc)

    pos = 0
    start_pos = 0
    edit_mode = False
    stop_pos = len(wordlists) - 1

    while pos <= stop_pos:
        """ Flush and clear console output. """
        os.system("clear")

        if not edit_mode:
            # get next word
            start, stop, _ = wordlists[pos]
        else:
            # reset edit_mode to False
            edit_mode = False

        print_colorful_description(desc, start, stop, entities)
        choice = readkey()

        if KEY_LEFT_ARROW == choice and pos != start_pos:
            # move to next word
            pos -= 1
        elif KEY_RIGHT_ARROW == choice and pos != stop_pos:
            # move to previous word
            pos += 1
        elif KEY_UP_ARROW == choice and pos != start_pos:
            # enter edit mode.
            start -= 1
            edit_mode = True
        elif KEY_DOWN_ARROW == choice and pos != stop_pos:
            # enter edit mode.
            stop += 1
            edit_mode = True
        elif "-" == choice and pos != start_pos:
            start += 1
            edit_mode = True
        elif "=" == choice and pos != stop_pos:
            # enter edit mode.
            stop -= 1
            edit_mode = True
        elif KEY_ENTER == choice:
            # enter next paragraph
            break
        elif "u" == choice:
            # unset current highlight
            match = [
                entry
                for entry in entities
                if (entry[0] == start)
                or (entry[1] == stop)
                or (entry[0] > start and entry[1] < stop)
            ]
            if match:
                entities.remove(match[0])
        elif "h" == choice:
            # print usage
            print_usage()
        elif "q" == choice:
            raise Exception
        elif choice in LABELS.keys():
            """ Add the labeled data into entities. """
            label = LABELS[choice]
            entry = [start, stop, label]
            if entry not in entities:
                entities.append([start, stop, label])

        if not edit_mode:
            # default clean start and stop value.
            start, stop = 0, 0

        # sort entities according the start index
        entities = sorted(entities, key=lambda x: x[0])
    return entities


def view_control(desc):
    """ wordlists: Store result extracted by regex. """
    wordlists = get_wordlists(desc)

    pos = 0
    start_pos = 0
    stop_pos = len(wordlists) - 1

    is_interesting = False

    while pos <= stop_pos:
        """ Flush and clear console output. """
        os.system("clear")
        start, stop, _ = wordlists[pos]

        print_colorful_description(desc, start, stop, [])
        choice = readkey()

        if KEY_LEFT_ARROW == choice and pos != start_pos:
            # move to next word
            pos -= 1
        elif KEY_RIGHT_ARROW == choice and pos != stop_pos:
            # move to previous word
            pos += 1
        elif KEY_UP_ARROW == choice and pos != start_pos:
            # enter edit mode.
            start -= 1
        elif KEY_DOWN_ARROW == choice and pos != stop_pos:
            # enter edit mode.
            stop += 1
        elif KEY_ENTER == choice:
            # enter next paragraph
            is_interesting = True
            break
        elif KEY_SPACE == choice:
            is_interesting = False
            break
        elif "q" == choice:
            raise Exception

    return is_interesting


@click.group()
def annotator():
    """ NER model dataset annotator utilities. """
    pass


@annotator.command()
@click.option(
    "-c",
    "--corpus",
    default="assets/ner/corpus.txt",
    type=click.Path(exists=True),
    help="path of raw corpus data for training nlp model.",
)
def flag(corpus):
    """ Label text whether if interested. """

    corpus = Path(corpus)
    """ Read descriptions and shuffle. """
    with open(corpus) as f:
        tweets = [line.strip() for line in f.readlines()]

    interesting_tweets_path = corpus.parent / "interesting_tweets.txt"
    with open(interesting_tweets_path) as f:
        interesting_tweets = set([line.strip() for line in f.readlines()])

    uninteresting_tweets_path = corpus.parent / "uninteresting_tweets.txt"
    with open(uninteresting_tweets_path) as f:
        uninteresting_tweets = set([line.strip() for line in f.readlines()])

    already_processed_tweets = interesting_tweets | uninteresting_tweets
    unprocessed_tweets = filter(lambda x: x not in already_processed_tweets, tweets)

    custom_tweets = filter(lambda x: "fuzz" in x, unprocessed_tweets)
    try:
        """ Iterate until get lines of specified number data. """
        for tweet in custom_tweets:
            is_interesting = view_control(tweet)

            write_file_path = (
                interesting_tweets_path if is_interesting else uninteresting_tweets_path
            )
            with open(write_file_path, "a") as f:
                f.write(tweet + "\n")
    except KeyboardInterrupt:
        print("Keyboard Interrupt.")
    except Exception as e:
        print(e)


@annotator.command()
@click.option(
    "-d",
    "--dataset",
    default="assets/report.json",
    type=click.Path(exists=True),
    help="dataset(report.json).",
)
@click.option("-i", "--index", default=0, type=int, help="Index start to annotation.")
def start(dataset, index):
    """ Fix existed dataset. """
    """ Read dataset. """
    datas = utils.load_json(dataset)

    start_index = index
    try:
        """ Iterate until get lines of specified number data. """
        for data in datas[start_index:]:
            """ entities: Store (start_index, end_index, word). """
            desc = data[0]
            entities = data[1]["entities"]
            """ Show and generate dataset word by word. """
            data[1]["entities"] = user_control(desc, entities=entities)
            index += 1
    except KeyboardInterrupt:
        print("Keyboard Interrupt.")
    except Exception as e:
        print(e)
    finally:
        print()
        print(symbol("➜"), white("(index) ="), white(str(index)))
        """ Dump the dataset to local. """
        utils.dump_json(datas, dataset)
