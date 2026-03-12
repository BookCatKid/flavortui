from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Static

from components.sidebar import Sidebar


class Explore(Vertical):

    DEFAULT_CSS = """
    Explore {
        layers: sidebar;
        overflow-y: auto;
    }

    Explore #title {
        text-align: center;
        text-style: bold;
        color: $text;
        margin: 2 0;
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield Sidebar()
        yield Static("Explore", id="title")
        yield Footer()
