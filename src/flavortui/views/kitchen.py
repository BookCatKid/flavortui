from textual.app import ComposeResult
from textual.containers import Grid, Vertical
from textual.widgets import Footer, Rule, Static

from flavortui.api.api import get_user
from flavortui.api.api_key import get_api_key
from flavortui.api.functions import format_seconds
from flavortui.components.sidebar import Sidebar
from flavortui.views.scroll_actions_mixin import ScrollActionsMixin

BANNER = """
███████╗██╗      █████╗ ██╗   ██╗ ██████╗ ██████╗ ████████╗ ██████╗ ██╗    ██╗███╗   ██╗
██╔════╝██║     ██╔══██╗██║   ██║██╔═══██╗██╔══██╗╚══██╔══╝██╔═══██╗██║    ██║████╗  ██║
█████╗  ██║     ███████║██║   ██║██║   ██║██████╔╝   ██║   ██║   ██║██║ █╗ ██║██╔██╗ ██║
██╔══╝  ██║     ██╔══██║╚██╗ ██╔╝██║   ██║██╔══██╗   ██║   ██║   ██║██║███╗██║██║╚██╗██║
██║     ███████╗██║  ██║ ╚████╔╝ ╚██████╔╝██║  ██║   ██║   ╚██████╔╝╚███╔███╔╝██║ ╚████║
╚═╝     ╚══════╝╚═╝  ╚═╝  ╚═══╝   ╚═════╝ ╚═╝  ╚═╝   ╚═╝    ╚═════╝  ╚══╝╚══╝ ╚═╝  ╚═══╝
"""

BANNER_WEIRD = """
███████╗██╗      █████╗ ██╗   ██╗ ██████╗ ██╗   ██╗██████╗ ████████╗ ██████╗ ██╗    ██╗███╗   ██╗
██╔════╝██║     ██╔══██╗██║   ██║██╔═══██╗██║   ██║██╔══██╗╚══██╔══╝██╔═══██╗██║    ██║████╗  ██║
█████╗  ██║     ███████║██║   ██║██║   ██║██║   ██║██████╔╝   ██║   ██║   ██║██║ █╗ ██║██╔██╗ ██║
██╔══╝  ██║     ██╔══██║╚██╗ ██╔╝██║   ██║██║   ██║██╔══██╗   ██║   ██║   ██║██║███╗██║██║╚██╗██║
██║     ███████╗██║  ██║ ╚████╔╝ ╚██████╔╝╚██████╔╝██║  ██║   ██║   ╚██████╔╝╚███╔███╔╝██║ ╚████║
╚═╝     ╚══════╝╚═╝  ╚═╝  ╚═══╝   ╚═════╝  ╚═════╝ ╚═╝  ╚═╝   ╚═╝    ╚═════╝  ╚══╝╚══╝ ╚═╝  ╚═══╝
"""


class StatCard(Static):
    DEFAULT_CSS = """
    StatCard {
        height: 8;
        border: tall $accent;
        content-align: center middle;
        text-align: center;
        background: $boost;
    }
    """


class Kitchen(ScrollActionsMixin, Vertical):
    can_focus = True

    BINDINGS = [
        ("j", "scroll_down", "Scroll Down"),
        ("k", "scroll_up", "Scroll Up"),
        ("g", "scroll_home", "Top"),
        ("G", "scroll_end", "Bottom"),
    ]

    DEFAULT_CSS = """
    Kitchen {
        layers: sidebar;
        overflow-y: auto;
    }

    Kitchen #banner {
        text-align: center;
        color: $warning;
        text-style: bold;
        margin: 1 0 0 0;
        height: auto;
    }

    Kitchen #greeting, #achievement-title {
        text-align: center;
        text-style: bold italic;
        color: $text;
        margin: 0 0 1 0;
        height: auto;
    }

    Kitchen .loading {
        text-align: center;
        margin: 2 0;
    }

    Kitchen Rule {
        margin: 1 4;
    }

    Kitchen #stats-grid {
        grid-size: 4;
        grid-gutter: 1 2;
        margin: 1 4;
        height: 10;
    }

    Kitchen #stats-grid-2 {
        grid-size: 2;
        grid-gutter: 1 2;
        margin: 1 4;
        height: 10;
    }

    Kitchen #stats-grid-3 {
        grid-size: 2;
        grid-gutter: 1 2;
        margin: 1 4;
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield Sidebar()
        yield Static("Loading...", classes="loading")
        yield Static("", id="greeting")
        yield Footer()

    def on_mount(self) -> None:
        self.run_worker(self._load_user, thread=True, exit_on_error=False)

    def _load_user(self) -> None:
        try:
            user = get_user(get_api_key())[1]
            self.app.call_from_thread(self._render_user, user)
        except Exception as e:
            self.app.call_from_thread(self._on_load_error, str(e))

    def _on_load_error(self, error):
        self.query_one(".loading", Static).update(f"Failed to load: {error}")

    def _render_user(self, user) -> None:
        self.app.update_offline_banner()
        self.query_one(".loading", Static).remove()
        greeting = self.query_one("#greeting", Static)

        if not user:
            greeting.update("❌ Failed to load user profile.")
            return

        footer = self.query_one(Footer)

        if self.app.settings["banner_mode"] == "weird":
            self.mount(Static(BANNER_WEIRD, id="banner"), before=greeting)
        else:
            self.mount(Static(BANNER, id="banner"), before=greeting)

        greeting.update(
            f"Welcome back, [bold cyan]{user['display_name']}[/bold cyan]! 🔥"
        )

        self.mount(Rule(), after=greeting)

        grid = Grid(id="stats-grid")
        self.mount(grid, before=footer)
        grid.mount_all(
            [
                StatCard(f"🍪\n\n[bold]{user['cookies']}[/bold] Cookies"),
                StatCard(f"👍\n\n[bold]{user['vote_count']}[/bold] Votes"),
                StatCard(f"💜\n\n[bold]{user['like_count']}[/bold] Likes"),
                StatCard(f"📁\n\n[bold]{len(user['project_ids'])}[/bold] Projects"),
            ]
        )

        grid2 = Grid(id="stats-grid-2")
        self.mount(grid2, before=footer)
        grid2.mount_all(
            [
                StatCard(
                    f"🕐\n[bold]{format_seconds(user['devlog_seconds_total'])}[/bold]\nTotal Devlog Time"
                ),
                StatCard(
                    f"🕐\n[bold]{format_seconds(user['devlog_seconds_today'])}[/bold]\nTime Today"
                ),
            ]
        )

        self.mount(Rule(), after=grid2)

        self.mount(Static("Achievements 🏆", id="achievement-title"), before=footer)

        grid3 = Grid(id="stats-grid-3")
        self.mount(grid3, before=footer)
        grid3.mount_all(
            StatCard(
                f"[bold]{achievement['name']}[/bold]\n\n{achievement['description']}"
            )
            for achievement in user["achievements"]
        )

        self.mount(Rule(), before=footer)
