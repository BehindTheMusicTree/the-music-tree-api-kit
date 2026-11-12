from typing import Any

from rest_framework.fields import ListField

from the_music_tree_api_kit.exception.validation.app.AppValidationException import AppValidationException

from .AppField import AppField


class AppListField(AppField, ListField):
    def __init__(self, **kwargs):
        ListField.__init__(self, **kwargs)
        self._child_field = None

    @property
    def child_field(self) -> Any:
        return self.child

    def get_error_field_name(self) -> str:
        return self.field_name or "list"

    def to_internal_value(self, data: Any) -> Any:
        if data is None:
            if not self.allow_null:
                self.fail("null")
            return None

        if not data:
            if not self.allow_empty:
                self.fail("required")
            return []

        if not isinstance(data, list):
            self.fail("not_a_list")

        return super().to_internal_value(data)

    def run_child_validation(self, data: list[Any]) -> list[Any]:
        # ListField would wrap a child's AppValidationException in an {index: detail} dict,
        # dropping its error code and attributing it to an unnamed field.
        validated = []
        for item in data:
            try:
                validated.append(self.child.run_validation(item))
            except AppValidationException as exc:
                raise AppValidationException(
                    message=exc.message,
                    field_validation_error_code=exc.field_validation_error_code,
                    field_name=self.get_error_field_name(),
                ) from exc
        return validated
