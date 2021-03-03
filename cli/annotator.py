import os
import re
import sys
import click
from loguru import logger
from rich import print
from readchar import readkey

from src import utils


def red(word):
    return f"[red]{word}[/red]"


def purple(word):
    return f"[purple]{word}[/purple]"


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
        f"[white]➡️️[/white] [white]([/white][yellow]{word}[/yellow][white]) = [/white]",
        end="",
    )
    """ flush to stdout. """
    sys.stdout.flush()


def print_label():
    print(
        "[white]️➡️ (label) = [/white]",
        "{}-{}".format(
            LABELS_COLOR["KEYWORD"]("k"),
            LABELS_COLOR["KEYWORD"]("KEYWORD"),
        ),
    )


def print_usage():
    print("\n\nhelp:")
    print("[white]⬆️ move forward one character.[/white]")
    print("[white]⬇️️ move backward one character.[/white]")
    print("[white]⬅️ move to previous word.[/white]")
    print("[white]️➡️️ move to next word.[/white]")
    print("[white]u unset the current highlighted word.[/white]")
    print("[white]q quit the annotator.[/white]")
    print("[white]🔄 go to the next paragraph.[/white]")

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
            raise KeyboardInterrupt
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

    with open("assets/features.txt") as f:
        keywords = set(word.strip() for word in f.readlines())

    try:
        """ Iterate until get lines of specified number data. """
        for data in dataset:
            """ entities: Store (start_index, end_index, word). """
            text = data[0]
            entities = data[1]["entities"]
            """ Show and generate dataset word by word. """
            data[1]["entities"] = user_control(text, entities=entities)
            for entity in data[1]["entities"]:
                keywords.add(entity[-1])
    except KeyboardInterrupt:
        print("Keyboard Interrupt.")
    except Exception as e:
        logger.exception(e)
    finally:
        print()
        """ Dump the dataset to local. """
        utils.dump_json(dataset, dataset_path)
        with open("assets/features.txt", "w") as f:
            for word in keywords:
                f.write(word + "\n")
