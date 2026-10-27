from typing import Self

from django.db import models

from .BaseManager import BaseManager
from .save_context import SaveContext


class BaseModel(models.Model):
    objects: BaseManager[Self]

    class Meta:
        abstract = True

    @staticmethod
    def _create_save_context(**kwargs):
        return SaveContext.create(**kwargs)

    def save(self, *args, **kwargs):
        adding = self._state.adding
        ctx = self._create_save_context(**kwargs)

        kwargs = self._prepare_save(ctx)
        self._perform_save(adding=adding, ctx=ctx)

        if ctx.should_track_fields:
            kwargs["update_fields"] = ctx.update_fields

        super().save(*args, **kwargs)
        self._post_save(adding=adding)

    def _prepare_save(self, ctx: SaveContext) -> dict:
        from .name_field_utils import transform_name_fields

        transformed_kwargs = transform_name_fields(self.__class__, **ctx.kwargs)
        ctx.kwargs = transformed_kwargs
        return ctx.kwargs

    def _perform_save(self, adding: bool, ctx: SaveContext) -> None:
        pass

    def _post_save(self, adding: bool) -> None:
        pass
