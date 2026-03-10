from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Label

from components.sidebar import Sidebar

TEXT = """I must not fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
I will permit it to pass over me and through me.
And when it has gone past, I will turn the inner eye to see its path.
Where the fear has gone there will be nothing. Only I will remain."""


class Homepage(Vertical):

    DEFAULT_CSS = """
    Homepage {
        layers: sidebar;
    }
    """

    def compose(self) -> ComposeResult:
        yield Sidebar()
        yield Label(TEXT)
        yield Footer()
