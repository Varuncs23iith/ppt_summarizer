import yaml
from box import Box
from pathlib import Path
from config import CONFIGS_DIRECTORY

config_paths = list(CONFIGS_DIRECTORY.glob("*.yaml"))

config = dict()
for path_ in config_paths:
    with open(path_, "r") as f:
        data = yaml.safe_load(f)
    config = config|data

config = Box(config)