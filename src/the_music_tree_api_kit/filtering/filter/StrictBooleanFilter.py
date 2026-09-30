from django import forms
from django.core.exceptions import ValidationError
from django_filters import BooleanFilter


class StrictNullBooleanField(forms.NullBooleanField):
    # TextInput passes the raw value through; NullBooleanSelect would map unknown values to None before to_python.
    widget = forms.TextInput
    default_error_messages = {"invalid": "Must be one of: true, false, 1, 0."}

    def to_python(self, value):
        if value in (None, ""):
            return None
        normalized = str(value).lower()
        if normalized in ("true", "1"):
            return True
        if normalized in ("false", "0"):
            return False
        raise ValidationError(self.error_messages["invalid"], code="invalid")


class StrictBooleanFilter(BooleanFilter):
    field_class = StrictNullBooleanField
