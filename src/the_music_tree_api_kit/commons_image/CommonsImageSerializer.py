from typing import Any

from rest_framework import serializers

from .Fields import Fields
from .validation import validate_commons_image

_KEYS = {"url", "page_url", "author", "license", "license_url"}


class CommonsImageSerializer(serializers.Serializer):
    """Nested input field for a Commons image (JSON bodies only: multipart cannot carry a nested object).

    Deliberately not an ``AppInputSerializer``: that base runs its body-wide duplicate-key check and reports unknown
    keys under their own name, so nesting it breaks any parent with a ``url`` / ``license`` field of its own. As a plain
    serializer, an error is reported by the parent under the nested field's name. The raw values go straight to
    ``validate_commons_image`` (no string coercion); ``null`` passes through when ``allow_null=True``.
    """

    def to_internal_value(self, data: Any) -> dict[str, Any]:
        if not isinstance(data, dict):
            raise serializers.ValidationError("image must be an object")
        unknown = sorted(set(data) - _KEYS)
        if unknown:
            raise serializers.ValidationError(f"unknown image key(s): {', '.join(unknown)}")
        error = validate_commons_image(data)
        if error is not None:
            raise serializers.ValidationError(error)
        return {key: data.get(key) for key in sorted(_KEYS)}
