from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal, Grid
from textual.widgets import Footer, Static, ProgressBar, Rule

from components.sidebar import Sidebar
from api.get_user import get_user
from api.api_key import get_api_key


BANNER = """
███████╗██╗      █████╗ ██╗   ██╗ ██████╗ ██████╗ ████████╗ ██████╗ ██╗    ██╗███╗   ██╗
██╔════╝██║     ██╔══██╗██║   ██║██╔═══██╗██╔══██╗╚══██╔══╝██╔═══██╗██║    ██║████╗  ██║
█████╗  ██║     ███████║██║   ██║██║   ██║██████╔╝   ██║   ██║   ██║██║ █╗ ██║██╔██╗ ██║
██╔══╝  ██║     ██╔══██║╚██╗ ██╔╝██║   ██║██╔══██╗   ██║   ██║   ██║██║███╗██║██║╚██╗██║
██║     ███████╗██║  ██║ ╚████╔╝ ╚██████╔╝██║  ██║   ██║   ╚██████╔╝╚███╔███╔╝██║ ╚████║
╚═╝     ╚══════╝╚═╝  ╚═╝  ╚═══╝   ╚═════╝ ╚═╝  ╚═╝   ╚═╝    ╚═════╝  ╚══╝╚══╝ ╚═╝  ╚═══╝
"""


def _format_seconds(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours}h {minutes}m"


class StatCard(Static):
    DEFAULT_CSS = """
    StatCard {
        height: 5;
        border: tall $accent;
        content-align: center middle;
        text-align: center;
        background: $boost;
    }
    """


class Homepage(Vertical):

    DEFAULT_CSS = """
    Homepage {
        layers: sidebar;
        overflow-y: auto;
    }

    Homepage #banner {
        text-align: center;
        color: $warning;
        text-style: bold;
        margin: 1 0 0 0;
        height: auto;
    }

    Homepage #greeting {
        text-align: center;
        text-style: bold italic;
        color: $text;
        margin: 0 0 1 0;
        height: auto;
    }

    Homepage Rule {
        margin: 0 4;
    }

    Homepage #stats-grid {
        grid-size: 4;
        grid-gutter: 1 2;
        margin: 1 4;
        height: auto;
    }

    Homepage #stats-grid-2 {
        grid-size: 2;
        grid-gutter: 1 2;
        margin: 1 4;
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield Sidebar()

        user = get_user(get_api_key())
        if not user:
            yield Static("❌ Failed to load user profile.", id="greeting")
            yield Footer()
            return

        yield Static(BANNER, id="banner")
        yield Static(f"Welcome back, [bold cyan]{user['display_name']}[/bold cyan]! 🔥", id="greeting")
        yield Rule()

        with Grid(id="stats-grid"):
            yield StatCard(f"🍪\n\n[bold]{user['cookies']}[/bold] Cookies")
            yield StatCard(f"👍\n\n[bold]{user['vote_count']}[/bold] Votes")
            yield StatCard(f"💜\n\n[bold]{user['like_count']}[/bold] Likes")
            yield StatCard(f"📁\n\n[bold]{len(user['project_ids'])}[/bold] Projects")

        with Grid(id="stats-grid-2"):
            yield StatCard(f"🕐\n[bold]{_format_seconds(user['devlog_seconds_total'])}[/bold]\nTotal Devlog Time")
            yield StatCard(f"🕐\n[bold]{_format_seconds(user['devlog_seconds_today'])}[/bold]\nTime Today")

        yield Rule()
        yield Footer()

    def on_mount(self) -> None:
        user = get_user(get_api_key())
        if not user:
            return
        today = user['devlog_seconds_today']
        goal_seconds = 8 * 3600
        progress = min(today / goal_seconds * 100, 100)
        try:
            bar = self.query_one("#devlog-bar", ProgressBar)
            bar.advance(progress)
        except Exception:
            pass
