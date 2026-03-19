from textual_image.widget import Image, HalfcellImage, SixelImage, UnicodeImage, TGPImage

IMAGE_WIDGETS = {
    "auto": Image,
    "halfcell": HalfcellImage,
    "sixel": SixelImage,
    "unicode": UnicodeImage,
    "tgp": TGPImage,
}


def ImageWrapper(image_path, app, **kwargs):
    ImageClass = IMAGE_WIDGETS.get(app.settings.get("image_mode", "auto"), Image)
    return ImageClass(image_path, **kwargs)
