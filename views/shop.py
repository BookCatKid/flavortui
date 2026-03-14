from textual.app import ComposeResult
from textual.containers import Vertical, Grid, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Footer, Static, Select, Input, Button, Label
from textual_image.widget import Image

from components.sidebar import Sidebar

from api.api import get_store
from api.api_key import get_api_key
from api.client import get_client

import webbrowser


class ShopCard(Vertical):
    DEFAULT_CSS = """
    ShopCard {
        width: 30;
        height: 18;
        border: tall $accent;
        text-align: center;
        background: $boost;
        padding: 1;
    }

    ShopCard Image {
        width: 100%;
        height: 10;
        min-height: 10;
        max-height: 10;
    }

    ShopCard Static.shop-text {
        height: 7;
    }

    ShopCard Static.shop-placeholder {
        height: 10;
        content-align: center middle;
    }
    """

    def __init__(self, image_path, shop_item, **kwargs):
        super().__init__(**kwargs)
        self._image_path = image_path
        self._name = shop_item["name"]
        self._price = shop_item["ticket_cost"]["base_cost"]
        self._sale_percentage = shop_item["sale_percentage"]
        self._real_price = self._price * (1 - (self._sale_percentage or 0) / 100)
        self._stock = shop_item["stock"]
        self._regions = shop_item["enabled"]
        self._shop_item = shop_item
        self._sort_name = self._name.lower()
        self._sort_price = self._price

    def compose(self) -> ComposeResult:
        if self._image_path:
            yield Image(self._image_path, classes="shop-image")
        else:
            yield Static("[italic]No image available[/italic]", classes="shop-placeholder")

        stock_display = f"Stock: {self._stock}" if self._stock is not None else ""

        if self._sale_percentage:
            price_line = (
                f"[italic][strike]{f"{self._price:.2f}".rstrip("0").rstrip('.')} 🍪[/strike][/italic]\t"
                f"[green]{f'{self._real_price:.2f}'.rstrip('0').rstrip('.')} 🍪[/green]"
            )
        else:
            price_line = f"{f'{self._price:.2f}'.rstrip('0').rstrip('.')} 🍪"

        text = (
            f"[bold]{self._name}[/bold]\n\n"
            f"{price_line}\n"
            f"[italic]{stock_display}[/italic]"
        )

        yield Static(
            text,
            classes="shop-text",
        )

    def on_click(self) -> None:
        self.app.push_screen(ShopItem(self._shop_item))

class ShopItem(ModalScreen):

    DEFAULT_CSS = """
    #dialog {
        grid-size: 2;
        grid-gutter: 1 2;
        grid-rows: 1fr 4;
        padding: 0 1;
        width: 90%;
        height: 90%;
        background: $surface;
    }

    #question {
        column-span: 2;
        height: 1fr;
        width: 1fr;
        content-align: center middle;
    }

    #button-container {
        column-span: 2;
        height: auto;
        margin-bottom: 1;
        align-horizontal: center;
    }

    #button-container Button {
        margin: 0 2;
    }
    """

    def __init__(self, shop_item, **kwargs):
        super().__init__(**kwargs)
        self._shop_item = shop_item

    def compose(self) -> ComposeResult:
        yield Grid(
            Label(self._shop_item["name"], id="question"),
            Horizontal(Button("Open on Web", variant="primary", id="open-web"), Button("Close", variant="primary", id="close"), id="button-container"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            self.app.exit()
        elif event.button.id == "open-web":
            webbrowser.open(f"https://flavortown.hackclub.com/shop/order?shop_item_id={self._shop_item['id']}")
        else:
            self.app.pop_screen()


class Shop(Vertical):

    DEFAULT_CSS = """
    Shop {
        layers: sidebar;
        overflow-y: auto;
    }

    Shop #title {
        text-align: center;
        text-style: bold;
        color: $text;
        margin: 2 0;
        height: auto;
    }

    Shop #loading {
        text-align: center;
        text-style: bold;
        color: $text;
        margin: 2 0;
        height: auto;
    }

    Shop #shop-grid {
        grid-size: 4;
        grid-gutter: 1 2;
        margin: 1 4;
        height: auto;
    }

    Shop .shop-image {
        width: 100%;
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield Sidebar()
        yield Static("Shop", id="title")
        yield Static("Loading...", id="loading")
        yield Footer()

    def on_mount(self):
        self._cards = []
        self.run_worker(self._load_store, thread=True)

    def _load_store(self):
        api_key = get_api_key()
        shop = get_store(api_key)[1]
        client = get_client(api_key)

        cards_data = []
        for item in shop:
            if item["buyable_by_self"] and item["type"] != "ShopItem::FreeStickers":
                image_path = client.fetch_image(item["image_url"])
                cards_data.append((image_path, item))

        self.app.call_from_thread(self._on_store_loaded, cards_data)

    def _on_store_loaded(self, cards_data):
        self.query_one("#loading", Static).remove()
        footer = self.query_one(Footer)
        self.mount(Input(placeholder="Search Items...", id="search-input"), before=footer)
        self.mount(Select(options=[("Name", "name"), ("Price", "price"), ("Arbitrary", "arbitrary")], prompt="Sort by", id="sort-select", value="price"), before=footer)
        self.mount(Select(
            options=[
                ("All Regions", "all"),
                ("United States", "us"),
                ("EU", "eu"),
                ("United Kingdom", "uk"),
                ("India", "in"),
                ("Canada", "ca"),
                ("Australia", "au"),
                ("Rest of World", "xx"),
            ],
            prompt="Region",
            id="region-select",
            value="all",
        ), before=footer)
        grid = Grid(id="shop-grid")
        self.mount(grid, before=footer)

        for image_path, item in cards_data:
            card = ShopCard(
                image_path,
                item,
            )
            self._cards.append(card)

        grid.mount_all(self._cards)
        self._apply_sort("price")

    def _apply_sort(self, sort_value) -> None:
        cards = [c for c in self._cards if c.display]
        if sort_value == "name":
            cards.sort(key=lambda c: c._sort_name)
        elif sort_value == "price":
            cards.sort(key=lambda c: c._sort_price)

        grid = self.query_one("#shop-grid", Grid)
        for i, card in enumerate(cards):
            grid.move_child(card, before=i)

    def on_select_changed(self, event: Select.Changed) -> None:
        if not self._cards:
            return
        if event.select.id in ("sort-select", "region-select"):
            self._refilter()

    def on_input_changed(self, event: Input.Changed):
        if not self._cards:
            return
        if event.input.id == "search-input":
            self._refilter()

    def _refilter(self) -> None:
        sort_value = self.query_one("#sort-select", Select).value
        region_value = self.query_one("#region-select", Select).value
        search_query = self.query_one("#search-input", Input).value.strip().lower()

        for card in self._cards:
            show = True
            if region_value != "all":
                if not card._regions.get(f"enabled_{region_value}", False):
                    show = False
            if search_query and search_query not in card._sort_name:
                show = False
            card.display = show

        self._apply_sort(sort_value)
