import webbrowser


from textual.app import ComposeResult
from textual.containers import Grid, Horizontal, Vertical
from textual.widgets import Button, Footer, Markdown, Static
from flavortui.views.scroll_actions_mixin import ScrollActionsMixin

from flavortui.api.api import get_project_devlogs, get_projects_for_user
from flavortui.api.api_key import get_api_key
from flavortui.api.functions import format_seconds, get_days_ago
from flavortui.components.image_wrapper import settings_image
from flavortui.components.popup_modal import PopupModal
from flavortui.components.sidebar import Sidebar

BASE_URL = "https://flavortown.hackclub.com"
FALLBACK_PROJECT_IMAGE = (
    "https://flavortown.hackclub.com/assets/default-banner-3d4e1b67.png"
)
STATUS_LABELS = {
    "submitted": "✅ Shipped",
    "draft": "📝 Draft",
}


def build_project_md(
    name,
    description,
    devlog_ids,
    ship_status,
    ai_declaration,
    max_len=150,
    created_at="",
    updated_at="",
) -> str:
    status = STATUS_LABELS.get(ship_status, ship_status)
    devlog_count = len(devlog_ids)
    devlog_label = "devlog" if devlog_count == 1 else "devlogs"
    short_desc = (
        f"{description[:max_len]}…" if len(description) > max_len else description
    )
    if created_at and updated_at:
        timing = f"Created {get_days_ago(created_at)} days ago, Updated {get_days_ago(updated_at)} days ago"
    else:
        timing = ""

    ai_declaration_text = f"🤖 {ai_declaration}" if ai_declaration else ""
    return (
        f"## {name}\n\n"
        f"{short_desc}\n\n"
        f"{status}  ·  {devlog_count} {devlog_label}\n\n"
        f"{timing}\n\n"
        f"{ai_declaration_text}"
    )


class ProjectCard(Vertical):
    can_focus = True
    BINDINGS = [("enter", "open_detail", "Open")]

    DEFAULT_CSS = """
    ProjectCard {
        width: 1fr;
        height: auto;
        border: round $accent;
        text-align: center;
        background: $boost;
        padding: 1;
    }

    ProjectCard:focus {
        border: thick $warning;
        background: $warning 15%;
    }

    ProjectCard .image-row {
        width: 100%;
        height: auto;
        align: center middle;
    }

    ProjectCard Image {
        width: auto;
        height: 10;
        min-height: 10;
        max-height: 10;
    }
    """

    def __init__(self, image_path, project, **kwargs):
        super().__init__(**kwargs)
        self._image_path = image_path
        self._project = project

    def compose(self) -> ComposeResult:
        img = settings_image(self._image_path, self.app)
        if img:
            with Horizontal(classes="image-row"):
                yield img
        yield Markdown(
            build_project_md(
                self._project["title"],
                self._project["description"],
                self._project["devlog_ids"],
                self._project["ship_status"],
                self._project["ai_declaration"],
                created_at=self._project["created_at"],
                updated_at=self._project["updated_at"],
            )
        )

    def action_open_detail(self):
        self.app.push_screen(ProjectItem(self._image_path, self._project))

    async def _on_click(self, event):
        self.app.push_screen(ProjectItem(self._image_path, self._project))


class DevlogRow(Vertical):
    DEFAULT_CSS = """
    DevlogRow {
        width: 100%;
        height: auto;
        border: round $accent;
        background: $boost;
        padding: 0 1 1 1;
        margin: 1 0;
    }

    DevlogRow Markdown {
        height: auto;
        margin-bottom: 1;
    }
    """

    def __init__(self, devlog, **kwargs):
        super().__init__(**kwargs)
        self._devlog = devlog

    def compose(self) -> ComposeResult:
        yield Static(
            f"{self._devlog['likes_count']} likes · {format_seconds(self._devlog['duration_seconds'])}\n\n"
        )
        yield Markdown(f"{self._devlog['body']}")
        for comment in self._devlog["comments"]:
            yield DevlogComment(comment)


class DevlogComment(Vertical):
    DEFAULT_CSS = """
    DevlogComment {
        width: 100%;
        height: auto;
        border: round $secondary;
    }
    """

    def __init__(self, comment, **kwargs):
        super().__init__(**kwargs)
        self._comment = comment

    def compose(self):
        yield Markdown(
            f"{self._comment['author']['display_name']}\n\n{self._comment['body']}"
        )


class ProjectItem(PopupModal):
    DEFAULT_CSS = """
    #project-header {
        height: auto;
        width: 100%;
    }

    #project-image-row {
        width: 100%;
        height: auto;
        align: center middle;
    }

    #project-image {
        width: auto;
        height: 12;
        min-height: 12;
        max-height: 12;
    }

    #project-title {
        text-align: center;
        text-style: bold;
        width: 100%;
        height: auto;
        margin: 1 0;
    }

    #project-info {
        height: auto;
        width: 100%;
        margin: 0 0 1 0;
        text-align: center;
    }

    #project-description {
        width: 100%;
        height: auto;
        margin: 0 0 1 0;
        text-align: center;
    }

    #item-long-description {
        padding: 1;
        border: round $accent;
        background: $boost;
    }

    #devlogs-container {
        height: auto;
        width: 100%;
    }

    .devlog-item {
        border: round $accent;
        background: $boost;
        margin: 1 0;
        padding: 1;
        height: auto;
    }

    .accessory-group {
        height: auto;
        width: 100%;
        margin: 0 0 1 0;
        align-horizontal: center;
    }

    .accessory-group-title {
        text-align: center;
        text-style: bold;
        width: 100%;
        height: auto;
        margin: 1 0;
    }

    .loading {
        text-align: center;
        margin: 2 0;
    }

    #link-buttons {
        height: auto;
        align-horizontal: center;
    }

    #link-buttons Button {
        margin: 0 2;
    }
    """

    def __init__(self, image_path, project_item, **kwargs):
        super().__init__(**kwargs)
        self._image_path = image_path
        self._project_item = project_item

    def compose_content(self) -> ComposeResult:
        name = self._project_item["title"]
        description = self._project_item["description"]
        devlog_ids = self._project_item["devlog_ids"]
        ship_status = self._project_item["ship_status"]
        ai_declaration = self._project_item.get("ai_declaration", "")
        created_at = self._project_item["created_at"]
        updated_at = self._project_item["updated_at"]

        with Vertical(id="project-header"):
            img = (
                settings_image(self._image_path, self.app, id="project-image")
                if self._image_path
                else None
            )
            if img:
                with Horizontal(id="project-image-row"):
                    yield img
            yield Static(f"[bold]{name}[/bold]", id="project-title")
        yield Markdown(
            build_project_md(
                name,
                description,
                devlog_ids,
                ship_status,
                ai_declaration,
                max_len=float("inf"),
                created_at=created_at,
                updated_at=updated_at,
            )
        )
        with Horizontal(id="link-buttons"):
            if self._project_item["demo_url"]:
                yield Button("Demo", id="demo-button", variant="primary")
            if self._project_item["repo_url"]:
                yield Button("Repo", id="repo-button", variant="primary")
            if self._project_item["readme_url"]:
                yield Button("Readme", id="readme-button", variant="primary")
        yield Static("Loading...", classes="loading")
        yield Vertical(id="devlogs-container")

    def compose_footer(self) -> ComposeResult:
        return [
            Button("Open on Web", variant="primary", id="open-web"),
            Button("Close", variant="primary", id="close"),
        ]

    def on_mount(self):
        self.run_worker(self._load_devlogs, thread=True, exit_on_error=False)

    def _load_devlogs(self):
        api_key = get_api_key()
        devlogs = get_project_devlogs(api_key, self._project_item["id"])[1]["devlogs"]
        self.app.call_from_thread(self._on_devlogs_loaded, devlogs)

    def _on_devlogs_loaded(self, devlogs):
        self.query_one(".loading", Static).remove()
        container = self.query_one("#devlogs-container", Vertical)
        for devlog in devlogs:
            container.mount(DevlogRow(devlog))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "open-web":
            webbrowser.open(
                f"https://flavortown.hackclub.com/projects/{self._project_item['id']}"
            )
        elif event.button.id == "demo-button":
            webbrowser.open(self._project_item["demo_url"])
        elif event.button.id == "repo-button":
            webbrowser.open(self._project_item["repo_url"])
        elif event.button.id == "readme-button":
            webbrowser.open(self._project_item["readme_url"])
        else:
            self.app.pop_screen()


class Projects(ScrollActionsMixin, Vertical):
    BINDINGS = [
        ("j", "scroll_down", "Scroll Down"),
        ("k", "scroll_up", "Scroll Up"),
        ("g", "scroll_home", "Top"),
        ("G", "scroll_end", "Bottom"),
    ]

    DEFAULT_CSS = """
    Projects {
        layers: sidebar;
        overflow-y: auto;
    }

    Projects #title {
        text-align: center;
        text-style: bold;
        color: $text;
        margin: 2 0;
        height: auto;
    }

    Projects .loading {
        text-align: center;
        margin: 2 0;
    }

    Projects #projects-grid {
        grid-size: 2;
        grid-gutter: 1 2;
        margin: 1 4;
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield Sidebar()
        yield Static("Projects", id="title")
        yield Static("Loading...", classes="loading")
        yield Footer()

    def on_mount(self):
        self.run_worker(self._load_projects, thread=True, exit_on_error=False)

    def _load_projects(self):
        try:
            api_key = get_api_key()
            projects = get_projects_for_user(api_key)

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

            self.app.call_from_thread(self._on_projects_loaded, cards_data)
        except Exception as e:
            self.app.call_from_thread(self._on_load_error, str(e))

    def _on_projects_loaded(self, cards_data):
        self.app.update_offline_banner()
        self.query_one(".loading", Static).remove()
        footer = self.query_one(Footer)
        grid = Grid(id="projects-grid")
        self.mount(grid, before=footer)
        cards = [ProjectCard(image_path, project) for image_path, project in cards_data]
        grid.mount_all(cards)

    def _on_load_error(self, error):
        self.query_one(".loading", Static).update(f"Failed to load: {error}")
