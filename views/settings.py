from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Footer, Static, Button

from components.api_key_input import ApiKeyInput
from components.sidebar import Sidebar


class Settings(Vertical):

    DEFAULT_CSS = """
    Settings {
        layers: sidebar;
        overflow-y: auto;
    }

    Settings #title {
        text-align: center;
        text-style: bold;
        color: $text;
        margin: 2 0;
        height: auto;
    }

    Settings #settings-container {
        height: auto;
        margin: 1 4;
    }

    Settings #settings-container Horizontal {
        height: auto;
        align-vertical: middle;
    }

    Settings #settings-container Static {
        width: auto;
        height: 3;
        content-align-vertical: middle;
        margin-right: 2;
    }

    Settings #settings-container Button {
        width: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield Sidebar()
        yield Static("Settings", id="title")
        with Vertical(id="settings-container"):
            with Horizontal():
                yield Static("Api key")
                yield Button("Edit Api Key", id="edit-api-key")
        yield Footer()

    def on_button_pressed(self, event):
        if event.button.id == "edit-api-key":
            if isinstance(self.app.screen, ApiKeyInput):
                self.app.pop_screen()
            self.app.push_screen(ApiKeyInput(lambda: None))
