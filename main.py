from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Static

from api.api import check_api_key
from api.api_key import get_api_key
from api.client import OfflineError, get_client
from api.settings import load_settings, save_settings
from components.api_key_input import ApiKeyInput
from components.sidebar import Sidebar
from views.explore import Explore
from views.kitchen import Kitchen
from views.projects import Projects
from views.settings import Settings
from views.shop import Shop


class FlavortownTUI(App):
    BINDINGS = [("s", "toggle_sidebar", "Toggle Sidebar")]

    show_sidebar = reactive(False)

    CSS = """
    Screen {
        align: center middle;
        background: $background 80%;
    }

    #offline-banner {
        dock: top;
        width: 100%;
        height: 1;
        background: $warning;
        color: $text;
        text-align: center;
        text-style: bold;
        display: none;
    }

    #offline-banner.-visible {
        display: block;
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

    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self._needs_api_key = False

    def update_setting(self, key: str, value) -> None:
        self.settings[key] = value
        save_settings(self.settings)

    def compose(self) -> ComposeResult:
        yield Static("⚡ Offline: using cached data", id="offline-banner")
        key = get_api_key()
        try:
            valid = key and check_api_key(key)
        except OfflineError:
            valid = bool(key)

        if valid:
            yield Kitchen()
        if not valid:
            self._needs_api_key = True

    def update_offline_banner(self) -> None:
        client = get_client(get_api_key(), self.settings)
        self.query_one("#offline-banner").set_class(client.is_offline, "-visible")

    def on_mount(self) -> None:
        if self._needs_api_key:
            self.push_screen(ApiKeyInput(lambda: self.mount(Kitchen())))

    VIEW_MAP = {
        "kitchen": Kitchen,
        "projects": Projects,
        "shop": Shop,
        "explore": Explore,
        "settings": Settings,
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
        self.query_one(Sidebar).set_class(show_sidebar, "-visible")


if __name__ == "__main__":
    FlavortownTUI().run()
