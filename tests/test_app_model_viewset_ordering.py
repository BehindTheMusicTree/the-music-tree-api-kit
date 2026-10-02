import uuid

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers
from rest_framework.test import APIRequestFactory, force_authenticate

from tests.fixture_app.models import FixtureCategory, FixtureItem
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


def _list_page(user, page):
    request = APIRequestFactory().get("/items/", {"page": page, "page_size": 2})
    force_authenticate(request, user=user)
    return _ItemViewSet.as_view({"get": "list"})(request)


@pytest.mark.django_db
def test_list_breaks_default_ordering_ties_by_pk_across_pages():
    user = get_user_model().objects.create(username="fixture-user")
    category = FixtureCategory.objects.create(user=user, _name="category")
    # Inserted in descending uuid order so insertion order and pk order disagree.
    uuids = sorted((uuid.uuid4() for _ in range(5)), reverse=True)
    for index, item_uuid in enumerate(uuids):
        FixtureItem.objects.create(uuid=item_uuid, user=user, _name=f"item {index}", category=category)
    FixtureItem.objects.update(created_on=timezone.now())

    listed = [item["uuid"] for page in (1, 2, 3) for item in _list_page(user, page).data["results"]]

    assert listed == [str(item_uuid) for item_uuid in sorted(uuids)]
