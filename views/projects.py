from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Static

from components.sidebar import Sidebar


class Projects(Vertical):

    DEFAULT_CSS = """
    Projects {
        layers: sidebar;
        overflow-y: auto;
    }

    Projects #title {
        text-align: center;
        text-style: bold;
        color: $text;
        margin: 2 0;
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield Sidebar()
        yield Static("Projects", id="title")
        yield Footer()
