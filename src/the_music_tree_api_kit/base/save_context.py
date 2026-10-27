from dataclasses import dataclass
from typing import Any


@dataclass
class SaveContext:
    """Context for save operations"""

    kwargs: dict[str, Any]
    modified_fields: list[str]
    update_fields: list[str] | None

    @staticmethod
    def create(**kwargs) -> SaveContext:
        """Factory method to create SaveContext instances"""
        update_fields = kwargs.get("update_fields")
        return SaveContext(
            kwargs=kwargs,
            modified_fields=[],
            update_fields=None if update_fields is None else list(update_fields),
        )

    @property
    def should_track_fields(self) -> bool:
        return self.update_fields is not None

    def add_modified_field(self, field: str) -> None:
        """Add a field to modified_fields and update_fields if needed"""
        self.modified_fields.append(field)
        if self.should_track_fields and field not in self.update_fields:
            self.update_fields.append(field)
