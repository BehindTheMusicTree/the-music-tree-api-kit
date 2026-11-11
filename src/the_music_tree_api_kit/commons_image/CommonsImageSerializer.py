from rest_framework import serializers

from the_music_tree_api_kit.serializer.AppInputSerializer import AppInputSerializer

from .validation import validate_commons_image


class CommonsImageSerializer(AppInputSerializer):
    """Nested input field for a Commons image. Values are checked by ``validate_commons_image``."""

    url = serializers.CharField(required=False, allow_null=True, allow_blank=True, trim_whitespace=False)
    page_url = serializers.CharField(required=False, allow_null=True, allow_blank=True, trim_whitespace=False)
    author = serializers.CharField(required=False, allow_null=True, allow_blank=True, trim_whitespace=False)
    license = serializers.CharField(required=False, allow_null=True, allow_blank=True, trim_whitespace=False)
    license_url = serializers.CharField(required=False, allow_null=True, allow_blank=True, trim_whitespace=False)

    def run_validation(self, data):
        # AppInputSerializer rejects None outright; a nullable nested image must pass it through.
        if data is None and self.allow_null:
            return None
        return super().run_validation(data)

    def validate(self, attrs):
        error = validate_commons_image(attrs)
        if error is not None:
            raise serializers.ValidationError(error)
        return attrs
