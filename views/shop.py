from textual.app import ComposeResult
from textual.containers import Vertical, Grid, Horizontal
from textual.widgets import Footer, Markdown, Static, Select, Input, Button
from components.image_wrapper import SettingsImage

from components.sidebar import Sidebar
from components.popup_modal import PopupModal

from api.api import get_store
from api.api_key import get_api_key
from api.client import get_client

import webbrowser


def format_price(price: float) -> str:
    return f"{price:.2f}".rstrip("0").rstrip(".")


def build_price_line(price: float, sale_percentage: float | None) -> str:
    if sale_percentage:
        real_price = price * (1 - sale_percentage / 100)
        return (
            f"[dim][italic][strike]{format_price(price)} 🍪[/strike][/italic][/dim]\t"
            f"[green]{format_price(real_price)} 🍪[/green]"
        )
    return f"{format_price(price)} 🍪"


def build_shop_text(name: str, price: float, sale_percentage: float | None, stock: int | None) -> str:
    stock_display = f"Stock: {stock}" if stock is not None else ""
    price_line = build_price_line(price, sale_percentage)
    return (
        f"[bold]{name}[/bold]\n\n"
        f"{price_line}\n"
        f"[italic]{stock_display}[/italic]"
    )


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

    def __init__(self, image_path, shop_item, shop_data, **kwargs):
        super().__init__(**kwargs)
        self._image_path = image_path
        self._shop_data = shop_data
        self._name = shop_item["name"]
        self._ticket_cost = shop_item["ticket_cost"]
        self._price = self._ticket_cost["base_cost"]
        self._sale_percentage = shop_item["sale_percentage"]
        self._real_price = self._price * (1 - (self._sale_percentage or 0) / 100)
        self._stock = shop_item["stock"]
        self._regions = shop_item["enabled"]
        self._shop_item = shop_item
        self._sort_name = self._name.lower()
        self._sort_price = self._price

    def _build_text(self) -> str:
        return build_shop_text(self._name, self._price, self._sale_percentage, self._stock)

    def compose(self) -> ComposeResult:
        img = SettingsImage(self._image_path, self.app, classes="shop-image")
        if img:
            yield img
        yield Static(self._build_text(), classes="shop-text")

    def set_region(self, region: str) -> None:
        if region == "all":
            self._price = self._ticket_cost["base_cost"]
        else:
            self._price = self._ticket_cost.get(region, self._ticket_cost["base_cost"])
        self._real_price = self._price * (1 - (self._sale_percentage or 0) / 100)
        self._sort_price = self._price
        self.query_one(".shop-text", Static).update(self._build_text())

    def on_click(self) -> None:
        self.app.push_screen(ShopItem(self._image_path, self._shop_item, self._shop_data))

class SubItemRow(Vertical):
    DEFAULT_CSS = """
    SubItemRow {
        width: 100%;
        height: auto;
        border: tall $accent;
        background: $boost;
        padding: 0 1;
        align-horizontal: center;
    }

    SubItemRow .sub-item-name {
        width: 100%;
        text-align: center;
    }

    SubItemRow .sub-item-price {
        width: 100%;
        text-align: center;
    }
    """

    def __init__(self, name: str, price: float, sale_percentage: float | None, **kwargs):
        super().__init__(**kwargs)
        self._name = name
        self._price = price
        self._sale_percentage = sale_percentage

    def compose(self) -> ComposeResult:
        yield Static(self._name, classes="sub-item-name")
        yield Static(build_price_line(self._price, self._sale_percentage), classes="sub-item-price")


class ShopItem(PopupModal):

    DEFAULT_CSS = """
    #item-header {
        height: auto;
        width: 100%;
    }

    #item-image-row {
        width: 100%;
        height: auto;
        align: center middle;
    }

    #item-image {
        width: auto;
        height: 12;
        min-height: 12;
        max-height: 12;
    }

    #item-title {
        text-align: center;
        text-style: bold;
        width: 100%;
        height: auto;
        margin: 1 0;
    }

    #item-info {
        height: auto;
        width: 100%;
        margin: 0 0 1 0;
        text-align: center;
    }

    #item-description {
        width: 100%;
        height: auto;
        margin: 0 0 1 0;
        text-align: center;
    }

    #item-long-description {
        padding: 1;
        border: tall $accent;
        background: $boost;
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
    """

    def __init__(self, image_path, shop_item, shop_data, **kwargs):
        super().__init__(**kwargs)
        self._image_path = image_path
        self._shop_item = shop_item
        self._shop_data = shop_data

    def _get_sub_items(self):
        sub_items = []
        for item in self._shop_data:
            if self._shop_item["id"] in item.get("attached_shop_item_ids", []):
                sub_items.append(item)
        return sub_items

    def _group_sub_items(self, sub_items):
        groups = {}
        for item in sub_items:
            tag = item.get("accessory_tag") or "other"
            groups.setdefault(tag, []).append(item)
        return groups

    def compose_content(self) -> ComposeResult:
        price = self._shop_item["ticket_cost"]["base_cost"]
        sale = self._shop_item["sale_percentage"]
        stock = self._shop_item["stock"]
        price_line = build_price_line(price, sale)
        stock_display = f"  ·  Stock: {stock}" if stock is not None else ""

        with Vertical(id="item-header"):
            img = SettingsImage(self._image_path, self.app, id="item-image") if self._image_path else None
            if img:
                with Horizontal(id="item-image-row"):
                    yield img
            yield Static(f"[bold]{self._shop_item['name']}[/bold]", id="item-title")
        yield Static(f"{price_line}{stock_display}", id="item-info")
        if self._shop_item.get("description"):
            yield Static(self._shop_item["description"], id="item-description")
        if self._shop_item.get("long_description"):
            yield Markdown(self._shop_item["long_description"], id="item-long-description")

        sub_items = self._get_sub_items()
        if sub_items:
            groups = self._group_sub_items(sub_items)
            for tag, items in groups.items():
                with Vertical(classes="accessory-group"):
                    yield Static(f"[bold]{tag.replace('_', ' ').title()}[/bold]", classes="accessory-group-title")
                    for item in items:
                        item_price = item["ticket_cost"]["base_cost"]
                        item_sale = item.get("sale_percentage")
                        yield SubItemRow(item["name"], item_price, item_sale)

    def compose_footer(self) -> ComposeResult:
        return [
            Button("Open on Web", variant="primary", id="open-web"),
            Button("Close", variant="primary", id="close")
        ]

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "open-web":
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

    Shop #sort-container {
        height: auto;
        align-vertical: middle;
    }

    Shop #sort-container Select {
        width: 1fr;
    }

    Shop #sort-container Button {
        min-width: 5;
        width: auto;
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
        self._reverse_sort = False
        self.run_worker(self._load_store, thread=True, exit_on_error=False)

    def _load_store(self):
        api_key = get_api_key()
        shop = get_store(api_key)[1]
        client = get_client(api_key)

        cards_data = []
        for item in shop:
            if item["buyable_by_self"] and item["type"] != "ShopItem::FreeStickers":
                image_path = client.fetch_image(item["image_url"])
                cards_data.append((image_path, item))

        self.app.call_from_thread(self._on_store_loaded, cards_data, shop)

    def _on_store_loaded(self, cards_data, shop_data):
        self.app.update_offline_banner()
        self.query_one("#loading", Static).remove()
        footer = self.query_one(Footer)
        self.mount(Input(placeholder="Search Items...", id="search-input"), before=footer)
        self.mount(Horizontal(
            Select(options=[("Name", "name"), ("Price", "price"), ("Arbitrary", "arbitrary")], prompt="Sort by", id="sort-select", value="price"),
            Button("↑", id="flip-sort"),
            id="sort-container"
        ), before=footer)
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

        self._shop_data = shop_data

        for image_path, item in cards_data:
            card = ShopCard(
                image_path,
                item,
                shop_data,
            )
            self._cards.append(card)

        grid.mount_all(self._cards)
        self._apply_sort("price")

    def _apply_sort(self, sort_value) -> None:
        cards = [c for c in self._cards if c.display]
        if sort_value == "name":
            cards.sort(key=lambda c: c._sort_name, reverse=self._reverse_sort)
        elif sort_value == "price":
            cards.sort(key=lambda c: c._sort_price, reverse=self._reverse_sort)
        elif sort_value == "arbitrary":
            if self._reverse_sort:
                cards.reverse()

        grid = self.query_one("#shop-grid", Grid)
        for i, card in enumerate(cards):
            grid.move_child(card, before=i)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "flip-sort":
            self._reverse_sort = not self._reverse_sort
            event.button.label = "↓" if self._reverse_sort else "↑"
            self._apply_sort(self.query_one("#sort-select", Select).value)
        elif event.button.id == "open-web":
            webbrowser.open(f"https://flavortown.hackclub.com/shop/order?shop_item_id={self._shop_item['id']}")
        elif event.button.id == "close":
            self.app.pop_screen()

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
            card.set_region(region_value)

        self._apply_sort(sort_value)
