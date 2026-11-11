from typing import Any

from .Fields import Fields

_KEY_BY_FIELD = {
    Fields.IMAGE_URL: "url",
    Fields.IMAGE_PAGE_URL: "page_url",
    Fields.IMAGE_AUTHOR: "author",
    Fields.IMAGE_LICENSE: "license",
    Fields.IMAGE_LICENSE_URL: "license_url",
}


def commons_image_kwargs(image: dict[str, Any] | None) -> dict[str, Any]:
    """Map an image object (or None) to the five column values; None clears every column."""
    image = image or {}
    return {field: image.get(key) for field, key in _KEY_BY_FIELD.items()}


def commons_image_representation(obj: Any) -> dict[str, Any] | None:
    """The image object for output, or None when the row has no image."""
    if getattr(obj, Fields.IMAGE_URL) is None:
        return None
    return {key: getattr(obj, field) for field, key in _KEY_BY_FIELD.items()}
