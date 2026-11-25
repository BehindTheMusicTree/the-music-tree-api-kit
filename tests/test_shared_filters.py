import json
from types import SimpleNamespace

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.test.utils import isolate_apps
from rest_framework import serializers
from rest_framework.test import APIRequestFactory, force_authenticate

from tests.fixture_app.models import FixtureCategory, FixtureItem
from the_music_tree_api_kit.exception.validation.app.AppValidationException import AppValidationException
from the_music_tree_api_kit.filtering.filter.char.NonEmptiableCharFilter import NonEmptiableCharFilter
from the_music_tree_api_kit.filtering.filter.char.OptionalEnumCharFilter import OptionalEnumCharFilter
from the_music_tree_api_kit.filtering.filter.char.RelatedObjectCharFilter import RelatedObjectCharFilter
from the_music_tree_api_kit.filtering.filter.foreign_key.DescendantAwareFilter import DescendantAwareFilter
from the_music_tree_api_kit.filtering.filter.foreign_key.ForeignKeyFilter import ForeignKeyFilter
from the_music_tree_api_kit.filtering.set.private_unique_resource.PrivateUniqueResourceFilterSet import (
    PrivateUniqueResourceFilterSet,
)
from the_music_tree_api_kit.view.error.exception_handler import custom_exception_handler
from the_music_tree_api_kit.view.viewset.model.AppModelViewSet import AppModelViewSet


class _Kind:
    ALONE = "alone"
    PAIRED = "paired"


class _ItemFilterSet(PrivateUniqueResourceFilterSet):
    name = NonEmptiableCharFilter(field_name="_name", field_name_public="name", lookup_expr="icontains")
    partner = ForeignKeyFilter(field_name="partner_category", field_name_public="partner")
    category = RelatedObjectCharFilter(primary_field="_name", field_name="category", field_name_public="category")
    related = RelatedObjectCharFilter(
        primary_field="_name", field_name="related_categories", field_name_public="related", lookup_expr="icontains"
    )
    kind = OptionalEnumCharFilter(enum_class=_Kind, method="filter_kind")

    class Meta:
        model = FixtureItem
        fields = ["name", "partner", "category", "related", "kind", *PrivateUniqueResourceFilterSet.get_date_fields()]

    def filter_kind(self, queryset, name, value):
        return queryset.filter(_name=value.lower())


class _ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FixtureItem
        fields = ["uuid"]


class _ItemViewSet(AppModelViewSet[FixtureItem]):
    def __init__(self, **kwargs):
        super().__init__(
            model_class=FixtureItem,
            simple_serializer_class=_ItemSerializer,
            detailed_serializer_class=_ItemSerializer,
            filterset_class=_ItemFilterSet,
            **kwargs,
        )

    def get_exception_handler(self):
        return custom_exception_handler

    def list(self, *args, **kwargs):
        return self._handle_list()


@pytest.fixture
def items():
    user = get_user_model().objects.create(username="fixture-user")
    category = FixtureCategory.objects.create(user=user, _name="Category")
    alone = FixtureItem.objects.create(user=user, _name="alone", category=category)
    paired = FixtureItem.objects.create(user=user, _name="paired", category=category, partner_category=category)
    return SimpleNamespace(user=user, category=category, alone=alone, paired=paired)


def _list(items, query):
    request = APIRequestFactory().get(f"/items/?{query}")
    force_authenticate(request, user=items.user)
    return _ItemViewSet.as_view({"get": "list"})(request)


def _uuids(response):
    assert response.status_code == 200, response.content
    return {row["uuid"] for row in response.data["results"]}


def _uuid_list(response):
    assert response.status_code == 200, response.content
    return [row["uuid"] for row in response.data["results"]]


def _error_codes(response):
    assert response.status_code == 400
    field_errors = json.loads(response.content)["details"]["fieldErrors"]
    return [error["code"] for errors in field_errors.values() for error in errors]


@pytest.mark.django_db
def test_filters_narrow_results(items):
    alone, paired = str(items.alone.uuid), str(items.paired.uuid)

    assert _uuids(_list(items, "")) == {alone, paired}
    assert _uuids(_list(items, "name=PAIR")) == {paired}
    assert _uuids(_list(items, "partner=")) == {alone}
    assert _uuids(_list(items, f"partner={items.category.pk}")) == {paired}
    assert _uuids(_list(items, "category=category")) == {alone, paired}
    assert _uuids(_list(items, "kind=ALONE")) == {alone}
    assert _uuids(_list(items, "created_on_gte=2999-01-01T00:00:00Z")) == set()


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("query", "code"),
    [("name=", "blank"), ("partner=not-a-uuid", "format_invalid"), ("kind=bogus", "enum_invalid")],
)
def test_invalid_values_are_rejected(items, query, code):
    assert _error_codes(_list(items, query)) == [code]


@pytest.mark.django_db
def test_foreign_key_error_uses_public_field_name(items):
    response = _list(items, "partner=not-a-uuid")
    assert response.status_code == 400
    assert list(json.loads(response.content)["details"]["fieldErrors"]) == ["partner"]


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("instance_pk", "is_descendant", "code"),
    [("self", False, "self_reference"), ("other", True, "ancestor_reference")],
)
def test_descendant_aware_filter_rejects_cycles(items, instance_pk, is_descendant, code):
    target = items.category
    instance = SimpleNamespace(
        pk=target.pk if instance_pk == "self" else "other", is_descendant_of=lambda _: is_descendant
    )
    descendant_filter = DescendantAwareFilter(field_name="pk", field_name_public="parent")
    descendant_filter.parent = SimpleNamespace(instance=instance, request=None)

    with pytest.raises(AppValidationException) as raised:
        descendant_filter.filter(FixtureCategory.objects.all(), str(target.pk))

    assert code in json.dumps(raised.value.detail)


@pytest.mark.django_db
def test_many_to_many_filter_lists_each_row_once(items):
    for name in ("Rock A", "Rock B"):
        items.paired.related_categories.add(FixtureCategory.objects.create(user=items.user, _name=name))

    response = _list(items, "related=rock")

    assert _uuid_list(response) == [str(items.paired.uuid)]
    assert response.data["overallTotal"] == 1


@pytest.mark.django_db
def test_many_to_many_filter_empty_value_lists_unlinked_rows(items):
    items.paired.related_categories.add(items.category)

    assert _uuid_list(_list(items, "related=")) == [str(items.alone.uuid)]


@pytest.mark.django_db
@pytest.mark.parametrize("relation", ["items", "related_items"])
def test_reverse_relation_is_rejected(relation):
    related_filter = RelatedObjectCharFilter(primary_field="_name", field_name=relation, field_name_public=relation)

    with pytest.raises(ImproperlyConfigured):
        related_filter.filter(FixtureCategory.objects.all(), "name")


@pytest.mark.parametrize("value", ["name", ""])
def test_nested_path_is_rejected(value):
    related_filter = RelatedObjectCharFilter(primary_field="_name", field_name="category__items", field_name_public="x")

    with pytest.raises(ImproperlyConfigured):
        related_filter.filter(FixtureItem.objects.all(), value)


@isolate_apps("tests.fixture_app")
def test_many_to_many_filter_follows_through_to_field():
    class Tag(models.Model):
        class Meta:
            app_label = "fixture_app"

        name = models.CharField(max_length=255)

    class Document(models.Model):
        class Meta:
            app_label = "fixture_app"

        code = models.IntegerField(unique=True)
        tags = models.ManyToManyField(Tag, through="DocumentTag")

    class DocumentTag(models.Model):
        class Meta:
            app_label = "fixture_app"

        document = models.ForeignKey(Document, to_field="code", on_delete=models.CASCADE)
        tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    tags_filter = RelatedObjectCharFilter(primary_field="name", field_name="tags", field_name_public="tags")

    sql = str(tags_filter.filter(Document.objects.all(), "rock").query)

    assert '"fixture_app_documenttag" U0' in sql
    assert 'U0."document_id" = ("fixture_app_document"."code")' in sql
