from textual.containers import Horizontal, Vertical

from textual.screen import ModalScreen
from flavortui.views.scroll_actions_mixin import ScrollActionsMixin
from textual.widgets import Button


class PopupModal(ScrollActionsMixin, ModalScreen):
    BINDINGS = [
        ("escape", "close_modal", "Close"),
        ("j", "scroll_down", "Scroll Down"),
        ("k", "scroll_up", "Scroll Up"),
        ("g", "scroll_home", "Top"),
        ("G", "scroll_end", "Bottom"),
    ]

    DEFAULT_CSS = """
    PopupModal {
        align: center middle;
    }

    #dialog {
        width: 80%;
        height: 90%;
        background: $surface;
        border: round $accent;
        padding: 1 2;
    }

    #dialog-content {
        overflow-y: auto;
        height: 1fr;
    }

    #project-header {
        height: auto;
        width: 100%;
    }

    #dialog-footer {
        height: auto;
        dock: bottom;
        align-horizontal: center;
        padding: 1 0;
    }

    #dialog-footer Button {
        margin: 0 2;
    }
    """

    def compose(self):
        with Vertical(id="dialog"):
            with Vertical(id="dialog-content"):
                yield from self.compose_content()
            with Horizontal(id="dialog-footer"):
                yield from self.compose_footer()

    def compose_content(self):
        return []

    def compose_footer(self):
        return [Button("Close", variant="primary")]

    def action_close_modal(self):
        self.app.pop_screen()

    def scroll_relative(self, y=0):
        self.query_one("#dialog-content").scroll_relative(y=y)

    def scroll_home(self, animate=False):
        self.query_one("#dialog-content").scroll_home(animate=animate)

    def scroll_end(self, animate=False):
        self.query_one("#dialog-content").scroll_end(animate=animate)
