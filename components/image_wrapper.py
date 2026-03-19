from textual_image.widget import Image, HalfcellImage, SixelImage, UnicodeImage, TGPImage

IMAGE_WIDGETS = {
    "auto": Image,
    "halfcell": HalfcellImage,
    "sixel": SixelImage,
    "unicode": UnicodeImage,
    "tgp": TGPImage,
}


def SettingsImage(image_path, app, **kwargs):
    mode = app.settings.get("image_mode", "auto")
    if mode == "none":
        return None
    ImageClass = IMAGE_WIDGETS.get(mode, Image)
    return ImageClass(image_path, **kwargs)
