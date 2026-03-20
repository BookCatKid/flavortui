import json
from pathlib import Path
from platformdirs import user_config_dir

SETTINGS_PATH = Path(user_config_dir("flavortui")) / "settings.json"
DEFAULTS = {
    "image_mode": "auto",
    "caching_strategy": "swr"
}


def load_settings() -> dict:
    if SETTINGS_PATH.exists():
        try:
            with open(SETTINGS_PATH) as f:
                saved = json.load(f)
            return {**DEFAULTS, **saved}
        except (json.JSONDecodeError, OSError):
            pass
    return dict(DEFAULTS)


def save_settings(settings: dict) -> None:
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=2)
