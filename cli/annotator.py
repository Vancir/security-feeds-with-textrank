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
KEY_ENTER = "\n"
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


def get_word_list(desc):
    word_list = []
    """ Get standalone word and strip some punctuation. """
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
        word_list.append([start, stop, word])
    return word_list


def user_control(text, entities=[]):
    """ word_list: Store result extracted by regex. """
    word_list = get_word_list(text)

    pos = 0
    start_pos = 0
    edit_mode = False
    stop_pos = len(word_list) - 1

    while pos <= stop_pos:
        """ Flush and clear console output. """
        os.system("clear")

        if not edit_mode:
            # get next word
            start, stop, _ = word_list[pos]
        else:
            # reset edit_mode to False
            edit_mode = False

        print_colorful_description(text, start, stop, entities)
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
            print("enter")
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


@click.command()
@click.option(
    "-d",
    "--dataset",
    default="assets/report.json",
    type=click.Path(exists=True),
    help="dataset(report.json).",
)
def annotator(dataset):
    """ Fix existed dataset. """
    """ Read dataset. """
    dataset_path = dataset
    dataset = utils.load_json(dataset)

    try:
        """ Iterate until get lines of specified number data. """
        for data in dataset:
            """ entities: Store (start_index, end_index, word). """
            text = data[0]
            entities = data[1]["entities"]
            """ Show and generate dataset word by word. """
            data[1]["entities"] = user_control(text, entities=entities)
    except KeyboardInterrupt:
        print("Keyboard Interrupt.")
    except Exception as e:
        print(e)
    finally:
        print()
        """ Dump the dataset to local. """
        utils.dump_json(dataset, dataset_path)
