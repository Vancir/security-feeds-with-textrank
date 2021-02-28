"""Get values / settings from local configuration."""

import yaml
from pathlib import Path
from loguru import logger
from typing import List, Optional

from src import environment

YAML_FILE_EXTENSION = ".yaml"
SEPARATOR = "."
PROJECT_PATH = "project"


def _load_yaml_file(yaml_file_path: Path):
    """Load yaml file and return parsed contents."""
    with open(yaml_file_path) as f:
        try:
            return yaml.safe_load(f.read())
        except Exception as e:
            logger.exception(e)


def _find_key_in_yaml_file(yaml_file_path: Path, search_keys: List[str]):
    """Find a key in a yaml file."""
    if not yaml_file_path.is_file():
        return None

    result = _load_yaml_file(yaml_file_path)

    if not search_keys:
        # Give the entire yaml file contents.
        # |value_is_relative_path| is not applicable here.
        return result

    for search_key in search_keys:
        if search_key not in result:
            return None

        result = result[search_key]

    return result


def _get_helper(key_name: Optional[str] = "", default=None):
    """Helper for get and get_absolute_functions."""
    if not key_name:
        logger.warning(f"Invalid config key: {key_name}")
        return default

    search_keys = key_name.split(SEPARATOR)
    yaml_path = environment.get_project_config()

    value = _find_key_in_yaml_file(yaml_path, search_keys)
    if value is None:
        return default

    return value


def get(key_name: Optional[str] = "", default=None):
    """Get key value using a key name."""
    return _get_helper(key_name, default=default)
