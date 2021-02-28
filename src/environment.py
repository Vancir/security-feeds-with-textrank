"""Environment functions."""
from pathlib import Path

PROJECT_CONFIG = "project.yaml"


def get_root_directory():
    """Return root directory."""
    root_dir = Path(__file__).parent.parent
    return root_dir


def get_project_config():
    """Return the path to the config directory."""
    return get_root_directory() / PROJECT_CONFIG


def get_assets_directory():
    """Return the path to the assets directory."""
    return get_root_directory() / "assets"
