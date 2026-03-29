from textual.app import ComposeResult
from textual.widgets import Static, Input, Button

from components.popup_modal import PopupModal
from api.api_key import get_api_key, save_api_key, delete_api_key
from api.api import check_api_key


class ApiKeyInput(PopupModal):
    DEFAULT_CSS = """
    #dialog {
        height: auto;
        max-height: 90%;
        padding: 2 4;
    }

    #dialog-content {
        height: auto;
        align-horizontal: center;
    }

    #title {
        text-align: center;
        width: 100%;
        margin-bottom: 1;
    }

    #subtitle {
        text-align: center;
        width: 100%;
        margin-bottom: 1;
    }
    """

    def __init__(self, callback_function, **kwargs):
        super().__init__(**kwargs)
        self._callback_function = callback_function

    def compose_content(self) -> ComposeResult:
        yield Static("🔒 Flavortown Api Key Required", id="title")
        yield Static("Please enter your api key to continue.", id="subtitle")
        yield Input(password=True, placeholder="Api Key")

    def compose_footer(self) -> ComposeResult:
        return [
            Button("Save API Key", id="save_key", variant="success"),
            Button("Print API Key", id="print_key", variant="primary"),
            Button("Delete API Key", id="delete_key", variant="error"),
            Button("Close", id="close", variant="default"),
        ]

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "save_key":
            self._save_key()
        elif event.button.id == "print_key":
            key = get_api_key()
            if key:
                self.notify(f"API Key: {key}", timeout=5.0)
            else:
                self.notify("No API key saved.", timeout=3.0)
        elif event.button.id == "delete_key":
            try:
                delete_api_key()
                self.notify("API key deleted successfully.", timeout=2.0)
            except Exception as e:
                self.notify(f"Error deleting API key: {e}", timeout=2.0)
        elif event.button.id == "close":
            self.app.pop_screen()

    def _save_key(self) -> None:
        value = self.query_one(Input).value
        if not value.strip():
            self.notify("API key cannot be empty.", timeout=2.0)
            return
        if not check_api_key(value):
            self.notify("Invalid API key. Please check and try again.", timeout=4.0)
            return
        try:
            save_api_key(value)
            self.notify("Api key saved successfully!", timeout=2.0)
            self.app.pop_screen()
            self._callback_function()
        except Exception as e:
            self.notify(f"Error saving api key: {e}", timeout=2.0)
