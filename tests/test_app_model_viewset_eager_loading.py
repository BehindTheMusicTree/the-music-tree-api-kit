import pytest
from django.contrib.auth import get_user_model
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework import serializers
from rest_framework.test import APIRequestFactory, force_authenticate

from tests.fixture_app.models import FixtureCategory, FixtureItem
from the_music_tree_api_kit.serializer.EagerLoadingMixin import EagerLoadingMixin
from the_music_tree_api_kit.view.viewset.model.AppModelViewSet import AppModelViewSet


class _CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FixtureCategory
        fields = ["uuid"]


class _ItemSerializer(EagerLoadingMixin, serializers.ModelSerializer):
    category = _CategorySerializer()

    @classmethod
    def setup_queryset(cls, queryset, prefix=""):
        return queryset.select_related(f"{prefix}category")

    class Meta:
        model = FixtureItem
        fields = ["uuid", "category"]


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

    def retrieve(self, *args, **kwargs):
        return self._handle_retrieve()


def _get(user, **kwargs):
    request = APIRequestFactory().get("/items/")
    force_authenticate(request, user=user)
    action = "retrieve" if kwargs else "list"
    return _ItemViewSet.as_view({"get": action})(request, **kwargs)


def _create_items(user, start, stop):
    for index in range(start, stop):
        category = FixtureCategory.objects.create(user=user, _name=f"category {index}")
        FixtureItem.objects.create(user=user, _name=f"item {index}", category=category)


@pytest.mark.django_db
def test_list_applies_serializer_eager_loading():
    user = get_user_model().objects.create(username="fixture-user")
    _create_items(user, 0, 1)
    with CaptureQueriesContext(connection) as one_item:
        _get(user)

    _create_items(user, 1, 6)
    with CaptureQueriesContext(connection) as many_items:
        response = _get(user)

    assert response.status_code == 200
    assert len(response.data["results"]) == 6
    assert len(many_items.captured_queries) == len(one_item.captured_queries)


@pytest.mark.django_db
def test_retrieve_applies_serializer_eager_loading():
    user = get_user_model().objects.create(username="fixture-user")
    _create_items(user, 0, 1)
    item = FixtureItem.objects.get()

    with CaptureQueriesContext(connection) as queries:
        response = _get(user, pk=str(item.uuid))

    assert response.status_code == 200
    assert response.data["category"]["uuid"] == str(item.category.uuid)
    assert not any(
        query["sql"].startswith('SELECT "fixture_app_fixturecategory"') for query in queries.captured_queries
    )
