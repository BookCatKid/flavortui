import shutil
from pathlib import Path
import webbrowser

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Select, Static

from flavortui.api.client import CACHE_DIR
from flavortui.api.settings import SETTINGS_DIR
from flavortui.components.api_key_input import ApiKeyInput
from flavortui.components.sidebar import Sidebar


class Settings(Vertical):
    DEFAULT_CSS = """
    Settings {
        layers: sidebar;
        overflow-y: auto;
    }

    Settings #title {
        text-align: center;
        text-style: bold;
        margin: 2 0;
        height: auto;
    }

    Settings .section {
        height: auto;
        margin: 1 4;
        padding: 1 2;
        background: $boost;
    }

    Settings .section-title {
        text-style: bold;
        color: $accent;
        height: auto;
        margin-bottom: 1;
    }

    Settings .setting-description {
        color: $text-muted;
        height: auto;
        margin-bottom: 1;
    }

    Settings .setting-row {
        height: auto;
        align-vertical: middle;
    }

    Settings .setting-label {
        width: 1fr;
        height: auto;
    }

    Settings #open-config-directory-button {
        margin-left: 2
    }
    """

    def compose(self) -> ComposeResult:
        yield Sidebar()
        yield Static("Settings", id="title")

        with Vertical(classes="section"):
            yield Static("Auth", classes="section-title")
            yield Static(
                "Reconfigure your flavortown api key. (or remove it!)",
                classes="setting-description",
            )
            yield Button("Edit API Key", id="edit-api-key")

        with Vertical(classes="section"):
            yield Static("Display", classes="section-title")
            yield Static(
                "Choose how images are rendered in the terminal. Some terminals will not support specific protocols, and will render weirdly when forced to use them. Auto will automatically find the best rendering option for your terminal. If you are experiencing lag, you might want to try different options and see what's best. Worst case scenario, they can be completely disabled!",
                classes="setting-description",
            )
            with Horizontal(classes="setting-row"):
                yield Static("Image Rendering mode", classes="setting-label")
                yield Select(
                    [
                        ("Auto (recommended)", "auto"),
                        ("Terminal Graphics Protocol (TGP)", "tgp"),
                        ("Unicode Half-Cell", "halfcell"),
                        ("Sixel", "sixel"),
                        ("Unicode", "unicode"),
                        ("None!", "none"),
                    ],
                    prompt="Image rendering mode",
                    value=self.app.settings["image_mode"],
                    id="image-rendering-select",
                )

        with Vertical(classes="section"):
            yield Static("Caching", classes="section-title")
            yield Static(
                "Control how often data is taken from the cache. Stale While Revalidate (SWR) is recommended because you get the best of both worlds: fast responses and up-to-date data. Timed will almost always show the most recent data, but will respect the API's rate limits. Extended is just timed but with 15x the timeout. If you want to always fetch the latest data, choose Never.",
                classes="setting-description",
            )
            with Horizontal(classes="setting-row"):
                yield Static("Caching Strategy", classes="setting-label")
                yield Select(
                    [
                        ("Stale While Revalidate (Recommended)", "swr"),
                        ("Timed/Rate Limited", "timed"),
                        ("Extended", "extended"),
                        ("Never (Not Recommended)", "never"),
                    ],
                    prompt="Caching Strategy",
                    value=self.app.settings["caching_strategy"],
                    id="caching-strategy-select",
                )
                yield Button("Clear Cache", id="clear-cache-button", variant="default")

        with Vertical(classes="section"):
            yield Static("Storage Directories", classes="section-title")
            with Horizontal(classes="setting-row"):
                yield Button("Open Cache Directory", id="open-cache-directory-button", variant="default")
                yield Button("Open Config Directory", id="open-config-directory-button", variant="default")

        yield Footer()

    def on_button_pressed(self, event):
        if event.button.id == "edit-api-key":
            if isinstance(self.app.screen, ApiKeyInput):
                self.app.pop_screen()
            self.app.push_screen(ApiKeyInput(lambda: None))
        if event.button.id == "clear-cache-button":
            if CACHE_DIR.is_dir():
                shutil.rmtree(CACHE_DIR)
        elif event.button.id == "open-cache-directory-button":
            if CACHE_DIR.is_dir():
                path = Path(CACHE_DIR).resolve()
                webbrowser.open(path.as_uri())
        elif event.button.id == "open-config-directory-button":
            if SETTINGS_DIR.is_dir():
                path = Path(SETTINGS_DIR).resolve()
                webbrowser.open(path.as_uri())


    def on_select_changed(self, event):
        if not isinstance(event.value, str):
            return
        if event.select.id == "image-rendering-select":
            self.app.update_setting("image_mode", event.value)
        elif event.select.id == "caching-strategy-select":
            self.app.update_setting("caching_strategy", event.value)
