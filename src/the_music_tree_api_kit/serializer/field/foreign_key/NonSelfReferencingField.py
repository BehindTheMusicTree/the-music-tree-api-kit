from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _

from the_music_tree_api_kit.exception.validation.app.AppValidationException import AppValidationException
from the_music_tree_api_kit.exception.validation.FieldValidationErrorCode import FieldValidationErrorCode
from the_music_tree_api_kit.uuid.UuidModel import UuidModel

from .PrivateUuidField import PrivateUuidField


class NonSelfReferencingField[T: models.Model](PrivateUuidField[T]):
    default_error_messages = {"self_reference": _("The object cannot reference itself.")}

    def to_internal_value(self, data: Any) -> T | None:
        referenced: UuidModel | None = PrivateUuidField.to_internal_value(self, data)
        if not referenced:
            return None

        instance = self.parent.instance

        if instance and referenced.uuid and instance.uuid == referenced.uuid:
            raise AppValidationException(
                field_name=str(self.field_name),
                message=self.error_messages["self_reference"],
                field_validation_error_code=FieldValidationErrorCode.SELF_REFERENCE,
            )

        return referenced
