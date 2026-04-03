import os
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

from PIL import Image as PILImage
from textual.containers import Vertical
from textual.widgets import Static
from textual_image.widget import (
    HalfcellImage,
    Image,
    SixelImage,
    TGPImage,
    UnicodeImage,
)

from flavortui.api.api_key import get_api_key
from flavortui.api.client import get_client

_IMAGE_POOL = ThreadPoolExecutor(max_workers=4)
THUMBNAIL_SIZE_PX = (256, 256)

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
        border: tall $panel-lighten-1;
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
        self.run_worker(self._load_image_pooled, thread=True, exit_on_error=False)

    def _load_image_pooled(self):
        future = _IMAGE_POOL.submit(self._resolve_and_preload, self._image_path)
        try:
            result = future.result()
            if result:
                self.app.call_from_thread(self._show_image, result)
            else:
                self.app.call_from_thread(self._show_unavailable)
        except Exception:
            self.app.call_from_thread(self._show_unavailable)

    def _resolve_and_preload(self, path):
        if not path:
            return None

        scheme = urlparse(path).scheme
        if scheme in {"http", "https"}:
            client = get_client(get_api_key(), self._app.settings)
            resolved = client.fetch_image(path)
        elif os.path.exists(path):
            resolved = path
        else:
            return None

        with PILImage.open(resolved) as pil_img:
            pil_img.load()
            converted_img = pil_img.convert("RGB")
        converted_img.thumbnail(THUMBNAIL_SIZE_PX)
        return converted_img

    def _show_image(self, pil_img):
        for child in list(self.children):
            child.remove()
        self.mount(self._image_class(pil_img, **self._image_kwargs))

    def _show_unavailable(self):
        placeholder = self.query_one(".image-placeholder", Static)
        placeholder.update("Image unavailable")


def settings_image(image_path, app, **kwargs):
    mode = app.settings.get("image_mode", "auto")
    if mode == "none":
        return None
    image_class = IMAGE_WIDGETS.get(mode, Image)
    return LazySettingsImage(image_path, app, image_class, kwargs)
