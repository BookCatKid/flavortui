from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static, Input


class ApiKeyInput(Vertical):

    DEFAULT_CSS = """
    ApiKeyInput {
        width: 75;
        height: auto;
        border: round cyan;
        padding: 1 2;
        background: $surface;
    }

    ApiKeyInput #title {
        text-align: center;
        margin-bottom: 1;
    }
    ApiKeyInput #subtitle {
        margin-bottom: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("🔒 Flavortown Api Key Required", id="title")
        yield Static("Please enter your api key to continue.", id="subtitle")
        yield Input(password=True, placeholder="Api Key")
