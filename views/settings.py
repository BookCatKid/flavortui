from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Static

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
    """

    def compose(self) -> ComposeResult:
        yield Sidebar()
        yield Static("Settings", id="title")
        yield Footer()
