from io import BytesIO

from textual.app import ComposeResult
from textual.containers import Vertical, Grid, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Footer, Static, Select, Input, Button, Label
from textual_image.widget import Image

from components.sidebar import Sidebar
from api.api import get_store
from api.api_key import get_api_key

from api.client import get_client


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

    def __init__(self, image_path, name, price, stock, shop_item, **kwargs):
        super().__init__(**kwargs)
        self._image_path = image_path
        self._name = name
        self._price = price
        self._stock = stock
        self._shop_item = shop_item

    def compose(self) -> ComposeResult:
        if self._image_path:
            yield Image(self._image_path, classes="shop-image")
        else:
            yield Static("[italic]No image available[/italic]", classes="shop-placeholder")

        stock_display = f"Stock: {self._stock}" if self._stock is not None else ""
        yield Static(
            f"[bold]{self._name}[/bold]\n\n{self._price} 🍪\n[italic]{stock_display}[/italic]",
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
            import webbrowser
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

    def on_mount(self) -> None:
        self._shop_data = None
        self.run_worker(self._load_store, thread=True)

    def _load_store(self) -> None:
        shop = get_store(get_api_key())[1]
        self.app.call_from_thread(self._on_store_loaded, shop)

    def _on_store_loaded(self, shop) -> None:
        self._shop_data = shop
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
        self.mount(Grid(id="shop-grid"), before=footer)
        self._render_shop(shop, "price", "all", "")

    def _format_shop_data(self, shop, sort, region, search):
        if region != "all":
            shop = [item for item in shop if item["enabled"][f"enabled_{region}"] == True]

        if sort == "name":
            shop.sort(key=lambda x: x["name"])
        elif sort == "price":
            shop.sort(key=lambda x: x["ticket_cost"]["base_cost"])

        if query := (search or "").strip().lower():
            shop = [item for item in shop if query in item["name"].lower()]

        return shop

    def _render_shop(self, shop, sort, region, search):
        grid = self.query_one("#shop-grid", Grid)
        grid.remove_children()

        shop = self._format_shop_data(shop, sort, region, search)

        for shop_item in shop:
            if shop_item["buyable_by_self"] and shop_item["type"] != "ShopItem::FreeStickers":
                name = shop_item["name"]
                price = shop_item["ticket_cost"]["base_cost"]
                stock = shop_item["stock"]
                image_path = get_client(get_api_key()).fetch_image(shop_item["image_url"])
                grid.mount(ShopCard(image_path, name, price, stock, shop_item))


    def on_select_changed(self, event: Select.Changed) -> None:
        if self._shop_data is None:
            return
        if event.select.id in ("sort-select", "region-select"):
            sort_value = self.query_one("#sort-select", Select).value
            region_value = self.query_one("#region-select", Select).value
            search_value = self.query_one("#search-input", Input).value
            self._render_shop(self._shop_data, sort_value, region_value, search_value)

    def on_input_changed(self, event: Input.Changed):
        if self._shop_data is None:
            return
        if event.input.id == "search-input":
            sort_value = self.query_one("#sort-select", Select).value
            region_value = self.query_one("#region-select", Select).value
            self._render_shop(self._shop_data, sort_value, region_value, event.value)
