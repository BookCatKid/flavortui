from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from components.api_key_input import ApiKeyInput
from components.sidebar import Sidebar
from views.kitchen import Kitchen
from views.projects import Projects
from views.shop import Shop
from views.explore import Explore
from views.settings import Settings
from textual.widgets import Input, Button

from api.api_key import get_api_key, save_api_key, delete_api_key
from api.api import check_api_key


class FlavortownTUI(App):

    BINDINGS = [("s", "toggle_sidebar", "Toggle Sidebar")]

    show_sidebar = reactive(False)

    CSS = """
    Screen {
        align: center middle;
        background: $background 80%;
    }

    #buttons {
        width: 75;
        height: auto;
        align: center middle;
        margin-top: 1;
    }

    #buttons Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        key = get_api_key()
        if key and check_api_key(key):
            yield Kitchen()
        else:
            yield ApiKeyInput()
            with Horizontal(id="buttons"):
                yield Button("Save API Key", id="save_key", variant="success")
                yield Button("Print API Key", id="print_key", variant="primary")
                yield Button("Delete API Key", id="delete_key", variant="error")

    def _show_kitchen(self) -> None:
        self.query("ApiKeyInput, #buttons").remove()
        self.mount(Kitchen())

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
            self._show_kitchen()
        except Exception as e:
            self.notify(f"Error saving api key: {e}", timeout=2.0)

    def on_input_submitted(self, event: Input.Submitted):
        self._save_key()

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

    VIEW_MAP = {
        "kitchen": Kitchen,
        "projects": Projects,
        "shop": Shop,
        "explore": Explore,
        "settings": Settings
    }

    def _switch_view(self, view_name: str) -> None:
        view_cls = self.VIEW_MAP.get(view_name)
        if not view_cls:
            return
        selector = ", ".join(v.__name__ for v in self.VIEW_MAP.values())
        current = self.query(selector)
        current.remove()
        self.mount(view_cls())
        self.show_sidebar = False

    def on_sidebar_navigate(self, message: Sidebar.Navigate) -> None:
        self._switch_view(message.view)

    def action_toggle_sidebar(self) -> None:
        self.show_sidebar = not self.show_sidebar

    def watch_show_sidebar(self, show_sidebar: bool) -> None:
        try:
            self.query_one(Sidebar).set_class(show_sidebar, "-visible")
        except Exception:
            pass


if __name__ == "__main__":
    FlavortownTUI().run()
