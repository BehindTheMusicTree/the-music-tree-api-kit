import json

import pytest
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.test import APIRequestFactory, force_authenticate

from tests.fixture_app.models import FixtureCategory, FixtureItem
from the_music_tree_api_kit.filtering.filter.StrictBooleanFilter import StrictBooleanFilter, StrictNullBooleanField
from the_music_tree_api_kit.filtering.set.AppFilterSet import AppFilterSet
from the_music_tree_api_kit.view.error.exception_handler import custom_exception_handler
from the_music_tree_api_kit.view.viewset.model.AppModelViewSet import AppModelViewSet


class _ItemFilterSet(AppFilterSet):
    has_no_partner = StrictBooleanFilter(field_name="partner_category", lookup_expr="isnull")
    has_no_category = StrictBooleanFilter(field_name="category", lookup_expr="isnull")

    class Meta:
        model = FixtureItem
        fields = []


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


def _list(query):
    user = get_user_model().objects.create(username="fixture-user")
    category = FixtureCategory.objects.create(user=user, _name="category")
    FixtureItem.objects.create(user=user, _name="alone", category=category)
    FixtureItem.objects.create(user=user, _name="paired", category=category, partner_category=category)
    request = APIRequestFactory().get(f"/items/?{query}")
    force_authenticate(request, user=user)
    return _ItemViewSet.as_view({"get": "list"})(request)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("true", True), ("TRUE", True), ("1", True), ("false", False), ("False", False), ("0", False), ("", None)],
)
def test_field_accepts_boolean_values_case_insensitively(raw, expected):
    assert StrictNullBooleanField(required=False).clean(raw) is expected


@pytest.mark.django_db
@pytest.mark.parametrize(("query", "count"), [("has_no_partner=TRUE", 1), ("has_no_partner=0", 1), ("", 2)])
def test_valid_values_filter(query, count):
    response = _list(query)

    assert response.status_code == 200
    assert len(response.data["results"]) == count


@pytest.mark.django_db
def test_invalid_value_is_rejected_as_invalid_filter():
    response = _list("has_no_partner=yes")

    assert response.status_code == 400
    field_errors = json.loads(response.content)["details"]["fieldErrors"]
    assert field_errors == {
        "hasNoPartner": [{"message": "Must be one of: true, false, 1, 0.", "code": "invalid_filter"}]
    }


@pytest.mark.django_db
def test_several_invalid_values_are_rejected_as_invalid_filters():
    response = _list("has_no_partner=yes&has_no_category=no")

    assert response.status_code == 400
    field_errors = json.loads(response.content)["details"]["fieldErrors"]
    assert field_errors == {
        "hasNoCategory, hasNoPartner": [{"message": "Invalid filter values detected", "code": "invalid_filters"}]
    }
