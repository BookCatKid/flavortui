from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Label

class Sidebar(Widget):
    DEFAULT_CSS = """
    Sidebar {
        width: 30;
        layer: sidebar;
        dock: left;
        offset-x: -100%;
        background: $primary;
        border-right: vkey $background;
        transition: offset 200ms;

        &.-visible {
            offset-x: 0;
        }

        & > Vertical {
            margin: 1 2;
        }
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Your sidebar here!")
