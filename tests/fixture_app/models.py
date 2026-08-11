from django.db import models

from the_music_tree_api_kit.base.BaseManager import BaseManager
from the_music_tree_api_kit.field.AppCharField import AppCharField
from the_music_tree_api_kit.field.foreign_key.PrivateForeignKey import PrivateForeignKey
from the_music_tree_api_kit.field.foreign_key.PrivateManyToManyField import PrivateManyToManyField
from the_music_tree_api_kit.field.foreign_key.PrivateOneToOneField import PrivateOneToOneField
from the_music_tree_api_kit.private_unique_resource.PrivateUniqueResource import PrivateUniqueResource


class FixtureCategoryManager(BaseManager):
    def get_default_ordering(self):
        return ["-created_on"]

    def delete_instance(self, instance):
        instance.delete()


class FixtureCategory(PrivateUniqueResource):
    _name = AppCharField(db_column="name", max_length=255)

    objects = FixtureCategoryManager()

    class Meta:
        app_label = "fixture_app"
        constraints = [
            models.UniqueConstraint(fields=["_name", "user"], name="unique_fixture_category_name_per_user"),
        ]


class FixtureItemManager(BaseManager):
    def get_default_ordering(self):
        return ["-created_on"]

    def delete_instance(self, instance):
        instance.delete()


class FixtureItem(PrivateUniqueResource):
    _name = AppCharField(db_column="name", max_length=255)
    category = PrivateForeignKey(FixtureCategory, on_delete=models.CASCADE, related_name="items")
    partner_category = PrivateOneToOneField(
        FixtureCategory, null=True, on_delete=models.SET_NULL, related_name="partner_item"
    )
    related_categories = PrivateManyToManyField(FixtureCategory, related_name="related_items")

    objects = FixtureItemManager()

    class Meta:
        app_label = "fixture_app"
