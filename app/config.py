import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
SETTINGS_PATH = BASE_DIR / "settings.json"

ALLOWED_ACTIONS = [
    "status",
    "is-active",
    "start",
    "stop",
    "restart",
]


def loadSettings(path=SETTINGS_PATH):
    with open(path, encoding="utf-8") as settingsFile:
        return json.load(settingsFile)


def getHosts():
    return loadSettings().get("hosts", {})


def getServices():
    return loadSettings().get("services", {})


def getActions():
    return ALLOWED_ACTIONS
