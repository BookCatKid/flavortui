from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Label, Button, Static
from textual.message import Message


class Sidebar(Widget):

    class Navigate(Message):
        def __init__(self, view: str) -> None:
            self.view = view
            super().__init__()

    DEFAULT_CSS = """
    Sidebar {
        width: 30;
        layer: sidebar;
        dock: left;
        offset-x: -100%;
        background: $boost;
        border-right: vkey $background;
        transition: offset 200ms;

        &.-visible {
            offset-x: 0;
        }

        & > Vertical {
            margin: 1 2;
            height: 100%;
        }

        & Label#sidebar-title {
            text-style: bold;
            color: $text;
            margin: 0 0 1 0;
        }

        & Button {
            width: 100%;
            margin: 0 0 1 0;
        }

        #spacer {
            height: 1fr;
        }
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Navigation", id="sidebar-title")
            yield Button("Kitchen", id="nav-kitchen")
            yield Button("Projects", id="nav-projects")
            yield Button("Shop", id="nav-shop")
            yield Button("Explore", id="nav-explore")
            yield Static(id="spacer")
            yield Button("Settings", id="nav-settings")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id and event.button.id.startswith("nav-"):
            view = event.button.id.removeprefix("nav-")
            self.post_message(self.Navigate(view))
            event.stop()
