import os
from urllib.parse import urlparse

from textual.containers import Vertical
from textual.widgets import Static
from textual_image.widget import Image, HalfcellImage, SixelImage, UnicodeImage, TGPImage

from api.api_key import get_api_key
from api.client import get_client

IMAGE_WIDGETS = {
    "auto": Image,
    "halfcell": HalfcellImage,
    "sixel": SixelImage,
    "unicode": UnicodeImage,
    "tgp": TGPImage,
}


class LazySettingsImage(Vertical):
    DEFAULT_CSS = """
    LazySettingsImage {
        height: auto;
        align: center middle;
    }

    LazySettingsImage .image-placeholder {
        width: 100%;
        height: 10;
        min-height: 10;
        max-height: 10;
        content-align: center middle;
        color: $text-muted;
        border: round $panel-lighten-1;
    }
    """

    def __init__(self, image_path, app, image_class, image_kwargs, **kwargs):
        super().__init__(**kwargs)
        self._image_path = image_path
        self._app = app
        self._image_class = image_class
        self._image_kwargs = image_kwargs

    def compose(self):
        yield Static("Loading image...", classes="image-placeholder")

    def on_mount(self):
        self.run_worker(self._load_image, thread=True, exit_on_error=False)

    def _resolve_path(self, path):
        if not path:
            return None

        scheme = urlparse(path).scheme
        if scheme in {"http", "https"}:
            client = get_client(get_api_key(), self._app.settings)
            return client.fetch_image(path)

        return path if os.path.exists(path) else None

    def _load_image(self):
        resolved_path = self._resolve_path(self._image_path)
        if resolved_path:
            self.app.call_from_thread(self._show_image, resolved_path)
        else:
            self.app.call_from_thread(self._show_unavailable)

    def _show_image(self, image_path):
        for child in list(self.children):
            child.remove()
        self.mount(self._image_class(image_path, **self._image_kwargs))

    def _show_unavailable(self):
        placeholder = self.query_one(".image-placeholder", Static)
        placeholder.update("Image unavailable")


def SettingsImage(image_path, app, **kwargs):
    mode = app.settings.get("image_mode", "auto")
    if mode == "none":
        return None
    ImageClass = IMAGE_WIDGETS.get(mode, Image)
    return LazySettingsImage(image_path, app, ImageClass, kwargs)
