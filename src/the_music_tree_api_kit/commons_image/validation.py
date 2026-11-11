from typing import Any

IMAGE_URL_LEN_MAX = 2048  # bytes


def _is_text(value: Any) -> bool:
    return isinstance(value, str) and value != ""


def _is_https_url(value: Any) -> bool:
    return _is_text(value) and value.startswith("https://") and len(value.encode()) <= IMAGE_URL_LEN_MAX


def validate_commons_image(image: Any) -> str | None:
    """Return the first error message for an image object (snake_case keys), or None when it is valid."""
    if not isinstance(image, dict):
        return "image must be an object"
    for key in ("url", "page_url"):
        if not _is_https_url(image.get(key)):
            return f"image {key} must be an https URL of at most {IMAGE_URL_LEN_MAX} bytes"
    if not _is_text(image.get("license")):
        return "image license must be a non-empty string"
    author = image.get("author")
    if author is not None and not _is_text(author):
        return "image author must be a non-empty string"
    # Commons serves some license URLs as plain http, so only the scheme is checked: the frontend links it.
    license_url = image.get("license_url")
    if license_url is not None and not (
        _is_text(license_url)
        and license_url.startswith(("http://", "https://"))
        and len(license_url.encode()) <= IMAGE_URL_LEN_MAX
    ):
        return f"image license_url must be an http(s) URL of at most {IMAGE_URL_LEN_MAX} bytes"
    return None
