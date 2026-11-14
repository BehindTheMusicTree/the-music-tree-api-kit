import uuid
from unittest.mock import Mock

import pytest
from django.contrib.auth import get_user_model
from django.http import Http404
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from tests.fixture_app.models import FixtureCategory
from the_music_tree_api_kit.exception.validation.app.AppValidationException import AppValidationException
from the_music_tree_api_kit.view.viewset.model.AppModelViewSet import AppModelViewSet

pytestmark = pytest.mark.django_db


@pytest.fixture
def detail():
    owner = get_user_model().objects.create(username="owner")
    other = get_user_model().objects.create(username="other")
    row = FixtureCategory.objects.create(user=owner, _name="visible")
    view = AppModelViewSet(model_class=FixtureCategory)
    view.request = Request(APIRequestFactory().get("/categories/"))
    view.request.user = owner
    view.request.owner = owner
    view.kwargs = {"pk": str(row.pk)}
    return view, row, other


def test_detail_uses_one_query_and_checks_permissions_once(detail, django_assert_num_queries):
    view, row, _ = detail
    view.check_object_permissions = Mock()
    with django_assert_num_queries(1):
        assert view.get_object() == row
    view.check_object_permissions.assert_called_once_with(view.request, row)


def test_hidden_row_is_not_found(detail):
    view, _, _ = detail
    view.get_queryset = FixtureCategory.objects.none
    with pytest.raises(Http404):
        view.get_object()


def test_private_lookup_cannot_read_another_owner(detail):
    view, _, other = detail
    view.request.owner = other
    # Even an override returning all rows must not broaden private ownership.
    view.get_queryset = FixtureCategory.objects.all
    with pytest.raises(Http404):
        view.get_object()


def test_public_lookup_still_honors_visibility(detail):
    view, row, other = detail
    view.is_private_resource = False
    view.request.owner = other
    assert view.get_object() == row
    view.get_queryset = FixtureCategory.objects.none
    with pytest.raises(Http404):
        view.get_object()


def test_denied_object_permission_is_enforced(detail):
    view, _, _ = detail
    view.check_object_permissions = Mock(side_effect=PermissionDenied)
    with pytest.raises(PermissionDenied):
        view.get_object()


def test_collection_filter_does_not_change_detail_lookup(detail):
    view, row, _ = detail
    view.filter_queryset = Mock(side_effect=AssertionError("collection filter called"))
    assert view.get_object() == row
    view.get_detail_queryset = FixtureCategory.objects.none
    with pytest.raises(Http404):
        view.get_object()


def test_custom_lookup_and_url_kwarg(detail):
    view, row, _ = detail
    view.lookup_field = "_name"
    view.lookup_url_kwarg = "name"
    view.kwargs = {"name": row._name}
    assert view.get_object() == row


@pytest.mark.parametrize("lookup", ["invalid", "00000000-0000-0000-0000-000000000000\n"])
def test_malformed_uuid_keeps_validation_contract(detail, lookup, django_assert_num_queries):
    view, _, _ = detail
    view.kwargs = {"pk": lookup}
    with django_assert_num_queries(0), pytest.raises(AppValidationException):
        view.get_object()


def test_missing_uuid_is_not_found_in_one_query(detail, django_assert_num_queries):
    view, _, _ = detail
    view.kwargs = {"pk": str(uuid.uuid4())}
    with django_assert_num_queries(1), pytest.raises(Http404):
        view.get_object()


def test_custom_uuid_lookup_rejects_malformed_value(detail):
    view, _, _ = detail
    view.lookup_field = "uuid"
    view.kwargs = {"uuid": "invalid"}
    with pytest.raises(Http404):
        view.get_object()


def test_ownerless_scope_cannot_read_owned_rows(detail):
    view, _, _ = detail
    view.request.owner = None
    with pytest.raises(Http404):
        view.get_object()


def test_uuid_object_lookup(detail):
    view, row, _ = detail
    view.kwargs = {"pk": row.pk}
    assert view.get_object() == row
