import json


def load_json(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        obj = json.load(f)
    return obj


def dump_json(obj, json_file, sort_keys=False):
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=sort_keys)
