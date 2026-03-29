from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal
from textual.widgets import Button


class PopupModal(ModalScreen):
    DEFAULT_CSS = """
    PopupModal {
        align: center middle;
    }

    #dialog {
        width: 80%;
        height: 90%;
        background: $surface;
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
