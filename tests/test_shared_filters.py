import json
from types import SimpleNamespace

import pytest
from django.contrib.auth import get_user_model
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
    kind = OptionalEnumCharFilter(enum_class=_Kind, method="filter_kind")

    class Meta:
        model = FixtureItem
        fields = ["name", "partner", "category", "kind", *PrivateUniqueResourceFilterSet.get_date_fields()]

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
