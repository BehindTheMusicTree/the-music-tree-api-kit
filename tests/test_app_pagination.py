import pytest
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.test import APIRequestFactory, force_authenticate

from tests.fixture_app.models import FixtureCategory, FixtureItem
from the_music_tree_api_kit.view.pagination.AppPagination import AppPagination
from the_music_tree_api_kit.view.viewset.model.AppModelViewSet import AppModelViewSet


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
            **kwargs,
        )

    def list(self, *args, **kwargs):
        return self._handle_list()


def _list(user, params):
    request = APIRequestFactory().get("/items/", params)
    force_authenticate(request, user=user)
    return _ItemViewSet.as_view({"get": "list"})(request)


@pytest.fixture
def user(db):
    user = get_user_model().objects.create(username="fixture-user")
    category = FixtureCategory.objects.create(user=user, _name="category")
    for index in range(5):
        FixtureItem.objects.create(user=user, _name=f"item {index}", category=category)
    return user


@pytest.mark.parametrize("value", ["0", "-1", "abc", ""])
def test_invalid_page_size_is_rejected(user, value):
    assert _list(user, {"page_size": value}).status_code == 400


def test_page_size_is_capped_at_max(user, settings):
    response = _list(user, {"page_size": 10**6})
    assert response.status_code == 200
    assert response.data["pageSize"] == AppPagination.max_page_size


def test_response_envelope(user):
    data = _list(user, {"page_size": 2, "page": 2}).data
    assert data["overallTotal"] == 5
    assert data["page"] == 2
    assert data["pageSize"] == 2
    assert data["totalPages"] == 3
    assert len(data["results"]) == 2


def test_paginated_response_schema():
    schema = AppPagination().get_paginated_response_schema({"type": "array"})
    assert set(schema["properties"]) == {
        "overallTotal",
        "next",
        "previous",
        "results",
        "page",
        "pageSize",
        "totalPages",
    }
    assert schema["properties"]["results"] == {"type": "array"}
