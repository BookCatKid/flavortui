import webbrowser

from textual.app import ComposeResult
from textual.containers import Grid, Horizontal, Vertical
from textual.widgets import (Button, Footer, Input, Markdown, Static,
                             TabbedContent, TabPane)

from flavortui.api.api import (get_devlogs, get_projects, get_projects_for_user,
                     get_user, get_users)
from flavortui.api.api_key import get_api_key
from flavortui.api.functions import format_seconds
from flavortui.components.image_wrapper import settings_image
from flavortui.components.popup_modal import PopupModal
from flavortui.components.sidebar import Sidebar
from flavortui.views.kitchen import StatCard
from flavortui.views.projects import (BASE_URL, FALLBACK_PROJECT_IMAGE, DevlogRow,
                            ProjectCard)


def build_users_md(display_name, cookies, project_ids):
    project_count = len(project_ids)
    project_label = "project" if project_count == 1 else "projects"
    cookies_line = f"🍪 {cookies} cookies" if cookies else "NO COOKIES!!! 💔"
    return f"## {display_name}\n\n{cookies_line}\n\n📁 {project_count} {project_label}"


class UserCard(Vertical):
    DEFAULT_CSS = """
    UserCard {
        width: 1fr;
        height: auto;
        border: tall $accent;
        text-align: center;
        background: $boost;
        padding: 1;
    }

    UserCard .image-row {
        width: 100%;
        height: auto;
        align: center middle;
    }

    UserCard Image {
        width: auto;
        height: 10;
        min-height: 10;
        max-height: 10;
    }
    """

    def __init__(self, image_path, user, **kwargs):
        super().__init__(**kwargs)
        self._image_path = image_path
        self._user = user

    def compose(self) -> ComposeResult:
        with Horizontal(classes="image-row"):
            if self._image_path:
                yield settings_image(self._image_path, self.app)
        yield Markdown(
            build_users_md(
                self._user["display_name"],
                self._user["cookies"],
                self._user["project_ids"],
            )
        )

    async def _on_click(self, event):
        self.app.push_screen(UserItem(self._image_path, self._user))


class UserItem(PopupModal):
    DEFAULT_CSS = """
    #user-header {
        width: 100%;
        height: auto;
    }

    #user-image-row {
        width: 100%;
        height: auto;
        align: center middle;
    }

    #user-image {
        width: auto;
        height: 12;
        min-height: 12;
        max-height: 12;
    }

    #user-title {
        text-align: center;
        text-style: bold;
        width: 100%;
        height: auto;
        margin: 1 0;
    }

    #user-overview {
        width: 100%;
        height: auto;
        text-align: center;
        margin: 0 0 1 0;
    }

    #user-stats-grid {
        grid-size: 4;
        grid-gutter: 1 2;
        margin: 1 0;
        height: auto;
    }

    #user-stats-grid-2 {
        grid-size: 2;
        grid-gutter: 1 2;
        margin: 1 0;
        height: auto;
    }

    #user-projects-title {
        text-align: center;
        text-style: bold;
        width: 100%;
        height: auto;
        margin: 1 0;
    }

    #user-projects-grid {
        grid-size: 2;
        grid-gutter: 1 2;
        height: auto;
    }

    .loading {
        text-align: center;
        margin: 2 0;
    }
    """

    def __init__(self, image_path, user, **kwargs):
        super().__init__(**kwargs)
        self._image_path = image_path
        self._user = user

    def compose_content(self) -> ComposeResult:
        with Vertical(id="user-header"):
            img = settings_image(self._image_path, self.app, id="user-image")
            if img:
                with Horizontal(id="user-image-row"):
                    yield img
            yield Static(f"[bold]{self._user['display_name']}[/bold]", id="user-title")
        yield Static("Loading...", classes="loading")
        yield Grid(id="user-stats-grid")
        yield Grid(id="user-stats-grid-2")
        yield Static("Projects", id="user-projects-title")
        yield Grid(id="user-projects-grid")

    def compose_footer(self) -> ComposeResult:
        return [
            Button("Open on Web", variant="primary", id="open-web"),
            Button("Close", variant="primary", id="close"),
        ]

    def on_mount(self):
        self.run_worker(self._load_user, thread=True, exit_on_error=False)

    def _load_user(self):
        try:
            api_key = get_api_key()
            user = get_user(api_key, self._user["id"])[1]
            projects = get_projects_for_user(api_key, self._user["id"])

            cards_data = []
            for _, project in projects:
                banner_url = project.get("banner_url")
                if banner_url:
                    if banner_url.startswith("/"):
                        banner_url = BASE_URL + banner_url
                    image_path = banner_url
                else:
                    image_path = FALLBACK_PROJECT_IMAGE
                cards_data.append((image_path, project))

            self.app.call_from_thread(self._on_user_loaded, user, cards_data)
        except Exception as e:
            self.app.call_from_thread(self._on_load_error, str(e))

    def _on_user_loaded(self, user, cards_data):
        self.query_one(".loading", Static).remove()

        stats = self.query_one("#user-stats-grid", Grid)
        stats.mount(StatCard(f"🍪\n\n[bold]{user.get('cookies') or 0}[/bold] Cookies"))
        stats.mount(StatCard(f"👍\n\n[bold]{user.get('vote_count', 0)}[/bold] Votes"))
        stats.mount(StatCard(f"💜\n\n[bold]{user.get('like_count', 0)}[/bold] Likes"))
        stats.mount(
            StatCard(f"📁\n\n[bold]{len(user.get('project_ids', []))}[/bold] Projects")
        )

        stats2 = self.query_one("#user-stats-grid-2", Grid)
        stats2.mount(
            StatCard(
                f"🕐\n[bold]{format_seconds(user.get('devlog_seconds_total', 0))}[/bold]\nTotal Devlog Time"
            )
        )
        stats2.mount(
            StatCard(
                f"🕐\n[bold]{format_seconds(user.get('devlog_seconds_today', 0))}[/bold]\nTime Today"
            )
        )

        projects_grid = self.query_one("#user-projects-grid", Grid)
        if cards_data:
            projects_grid.mount_all(
                [ProjectCard(image_path, project) for image_path, project in cards_data]
            )
        else:
            projects_grid.mount(Static("No projects yet."))

    def _on_load_error(self, error):
        self.query_one(".loading", Static).update(f"Failed to load: {error}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "open-web":
            webbrowser.open(f"https://flavortown.hackclub.com/users/{self._user['id']}")
            return
        self.app.pop_screen()


CHUNK_SIZE = 20


class Explore(Vertical):
    DEFAULT_CSS = """
    Explore {
        layers: sidebar;
        overflow-y: auto;
    }

    Explore #title {
        text-align: center;
        text-style: bold;
        color: $text;
        margin: 2 0;
        height: auto;
    }

    Explore .loading {
        text-align: center;
        margin: 2 0;
    }

    Explore TabbedContent {
        height: 1fr;
    }

    Explore ContentSwitcher {
        height: 1fr;
    }

    Explore TabPane {
        height: 1fr;
        overflow-y: auto;
    }

    Explore #projects-grid {
        grid-size: 2;
        grid-gutter: 1 2;
        margin: 1 4;
        height: auto;
    }

    Explore #devlogs-grid {
        grid-size: 1;
        grid-gutter: 1;
        margin: 1 4;
        height: auto;
    }

    Explore #users-grid {
        grid-size: 2;
        grid-gutter: 1 2;
        margin: 1 4;
        height: auto;
    }

    Explore .load-more {
        width: 100%;
        margin: 1 4;
        display: none;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._all_projects = []
        self._all_devlogs = []
        self._all_users = []
        self._projects_offset = 0
        self._devlogs_offset = 0
        self._users_offset = 0
        self._devlogs_loaded = False
        self._users_loaded = False

    def compose(self) -> ComposeResult:
        yield Sidebar()
        yield Static("Explore", id="title")
        with TabbedContent():
            with TabPane("Projects", id="projects-pane"):
                yield Input(placeholder="Search Items...", id="projects-search-input")
                yield Static("Loading...", classes="loading")
                yield Grid(id="projects-grid")
                yield Button("Load more", id="projects-load-more", classes="load-more")
            with TabPane("Devlogs", id="devlogs-pane"):
                yield Static("Loading...", classes="loading")
                yield Grid(id="devlogs-grid")
                yield Button("Load more", id="devlogs-load-more", classes="load-more")
            with TabPane("Users", id="users-pane"):
                yield Input(placeholder="Search Users...", id="users-search-input")
                yield Static("Loading...", classes="loading")
                yield Grid(id="users-grid")
                yield Button("Load more", id="users-load-more", classes="load-more")
        yield Footer()

    def on_mount(self):
        self.run_worker(self._load_explore, thread=True, exit_on_error=False)

    def _load_explore(self):
        self._load_projects()

    def _on_projects_loaded(self):
        self.app.update_offline_banner()
        self.query_one("#projects-pane .loading", Static).display = False

        grid = self.query_one("#projects-grid", Grid)
        visible_projects = self._all_projects[
            self._projects_offset : self._projects_offset + CHUNK_SIZE
        ]
        cards = [
            ProjectCard(image_path, project) for image_path, project in visible_projects
        ]
        grid.mount_all(cards)
        self.query_one("#projects-load-more").display = (
            self._projects_offset + CHUNK_SIZE < len(self._all_projects)
        )

    def _load_devlogs(self):
        try:
            api_key = get_api_key()
            _, data = get_devlogs(api_key)
            devlogs = data.get("devlogs", [])
            self._all_devlogs = devlogs
            self.app.call_from_thread(self._on_devlogs_loaded)
        except Exception as e:
            self.app.call_from_thread(self._on_load_error, str(e), "devlogs-pane")

    def _load_projects(self, query=""):
        try:
            api_key = get_api_key()
            _, data = get_projects(api_key, query=query)
            projects = data.get("projects", [])

            cards_data = []
            for project in projects:
                banner_url = project.get("banner_url")
                if banner_url:
                    if banner_url.startswith("/"):
                        banner_url = BASE_URL + banner_url
                    image_path = banner_url
                else:
                    image_path = FALLBACK_PROJECT_IMAGE
                cards_data.append((image_path, project))

            self._all_projects = cards_data
            self.app.call_from_thread(self._on_projects_loaded)
        except Exception as e:
            self.app.call_from_thread(self._on_load_error, str(e), "projects-pane")

    def _on_devlogs_loaded(self):
        self.query_one("#devlogs-pane .loading", Static).display = False
        self.query_one("#devlogs-load-more").display = (
            self._devlogs_offset + CHUNK_SIZE < len(self._all_devlogs)
        )
        grid = self.query_one("#devlogs-grid", Grid)
        visible_devlogs = self._all_devlogs[
            self._devlogs_offset : self._devlogs_offset + CHUNK_SIZE
        ]
        cards = [DevlogRow(devlog) for devlog in visible_devlogs]
        grid.mount_all(cards)
        self._devlogs_loaded = True

    def _load_users(self, query=""):
        try:
            api_key = get_api_key()
            _, data = get_users(api_key, query=query)
            users = data.get("users", [])

            cards_data = []
            for user in users:
                avatar_url = user.get("avatar")
                image_path = avatar_url or None
                cards_data.append((image_path, user))

            self._all_users = cards_data
            self.app.call_from_thread(self._on_users_loaded)
        except Exception as e:
            self.app.call_from_thread(self._on_load_error, str(e), "users-pane")

    def _on_users_loaded(self):
        self.query_one("#users-pane .loading", Static).display = False
        self.query_one("#users-load-more").display = (
            self._users_offset + CHUNK_SIZE < len(self._all_users)
        )
        grid = self.query_one("#users-grid", Grid)
        visible_users = self._all_users[
            self._users_offset : self._users_offset + CHUNK_SIZE
        ]
        cards = [UserCard(image_path, user) for image_path, user in visible_users]
        grid.mount_all(cards)
        self._users_loaded = True

    def _on_load_error(self, error, pane_id=None):
        if pane_id:
            self.query_one(f"#{pane_id} .loading", Static).update(
                f"Failed to load: {error}"
            )
        else:
            self.query_one(".loading", Static).update(f"Failed to load: {error}")

    def _show_next_projects_chunk(self):
        if self._projects_offset + CHUNK_SIZE >= len(self._all_projects):
            return
        self._projects_offset += CHUNK_SIZE
        self._on_projects_loaded()

    def _show_next_devlogs_chunk(self):
        if self._devlogs_offset + CHUNK_SIZE >= len(self._all_devlogs):
            return
        self._devlogs_offset += CHUNK_SIZE
        self._on_devlogs_loaded()

    def _show_next_users_chunk(self):
        if self._users_offset + CHUNK_SIZE >= len(self._all_users):
            return
        self._users_offset += CHUNK_SIZE
        self._on_users_loaded()

    def on_button_pressed(self, event):
        if event.button.id == "projects-load-more":
            self._show_next_projects_chunk()
        elif event.button.id == "devlogs-load-more":
            self._show_next_devlogs_chunk()
        elif event.button.id == "users-load-more":
            self._show_next_users_chunk()

    def on_input_submitted(self, event):
        if event.input.id == "projects-search-input":
            self._projects_offset = 0
            self.query_one("#projects-pane .loading", Static).display = True
            self.query_one("#projects-grid", Grid).remove_children()
            self.query_one("#projects-load-more").display = False
            self.run_worker(
                lambda: self._load_projects(event.input.value.strip()),
                thread=True,
                exit_on_error=False,
            )

        if event.input.id == "users-search-input":
            self._users_offset = 0
            self.query_one("#users-pane .loading", Static).display = True
            self.query_one("#users-grid", Grid).remove_children()
            self.query_one("#users-load-more").display = False
            self.run_worker(
                lambda: self._load_users(event.input.value.strip()),
                thread=True,
                exit_on_error=False,
            )

    async def on_tabbed_content_tab_activated(self, event):
        if event.pane.id == "devlogs-pane" and not getattr(
            self, "_devlogs_loaded", False
        ):
            self.run_worker(self._load_devlogs, thread=True, exit_on_error=False)
        elif event.pane.id == "users-pane" and not getattr(
            self, "_users_loaded", False
        ):
            self.run_worker(self._load_users, thread=True, exit_on_error=False)
