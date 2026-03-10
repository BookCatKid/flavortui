from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static


class Homepage(Vertical):

    DEFAULT_CSS = """
    Homepage {
        align: center middle;
    }

    Homepage #welcome {
        text-align: center;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("Welcome to FlavorTUI!", id="welcome")
