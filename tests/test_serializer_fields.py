import pytest
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from tests.fixture_app.models import FixtureCategory
from the_music_tree_api_kit.exception.validation.app.AppValidationException import AppValidationException
from the_music_tree_api_kit.exception.validation.FieldValidationErrorCode import FieldValidationErrorCode
from the_music_tree_api_kit.serializer.AppInputSerializer import AppInputSerializer
from the_music_tree_api_kit.serializer.field.AppCharField import AppCharField
from the_music_tree_api_kit.serializer.field.foreign_key.NonSelfReferencingField import NonSelfReferencingField


class FixtureCategoryInputSerializer(AppInputSerializer):
    name = AppCharField(max_length=255)
    parent = NonSelfReferencingField(queryset=FixtureCategory.objects.all(), required=False, allow_null=True)


def _drf_request(user):
    django_request = APIRequestFactory().post("/fixture-categories/", data={}, content_type="application/json")
    request = Request(django_request)
    request.user = user
    return request


@pytest.mark.django_db
def test_app_input_serializer_raises_app_validation_exception_on_blank_field():
    user = get_user_model().objects.create(username="fixture-user")
    request = _drf_request(user)

    serializer = FixtureCategoryInputSerializer(data={"name": ""}, context={"request": request})
    with pytest.raises(ValidationError) as exc_info:
        serializer.is_valid(raise_exception=True)

    converted = AppValidationException._detect_and_convert_from_drf_exception(exc_info.value)
    assert converted is not None
    assert converted.field == "name"
    assert converted.errors["name"]["code"] == FieldValidationErrorCode.BLANK


@pytest.mark.django_db
def test_app_input_serializer_rejects_unknown_field():
    user = get_user_model().objects.create(username="fixture-user")
    request = _drf_request(user)

    serializer = FixtureCategoryInputSerializer(data={"name": "genre", "bogus": "x"}, context={"request": request})
    with pytest.raises(ValidationError) as exc_info:
        serializer.is_valid(raise_exception=True)

    converted = AppValidationException._detect_and_convert_from_drf_exception(exc_info.value)
    assert converted is not None
    assert converted.errors["bogus"]["code"] == FieldValidationErrorCode.UNKNOWN


@pytest.mark.django_db
def test_non_self_referencing_field_rejects_self_reference():
    user = get_user_model().objects.create(username="fixture-user")
    category = FixtureCategory.objects.create(user=user, _name="genre")
    request = _drf_request(user)

    serializer = FixtureCategoryInputSerializer(
        instance=category, data={"name": "genre", "parent": str(category.pk)}, context={"request": request}
    )

    with pytest.raises(ValidationError) as exc_info:
        serializer.is_valid(raise_exception=True)

    converted = AppValidationException._detect_and_convert_from_drf_exception(exc_info.value)
    assert converted is not None
    assert converted.errors["parent"]["code"] == FieldValidationErrorCode.SELF_REFERENCE


@pytest.mark.django_db
def test_non_self_referencing_field_accepts_other_reference():
    user = get_user_model().objects.create(username="fixture-user")
    parent = FixtureCategory.objects.create(user=user, _name="parent-genre")
    child = FixtureCategory.objects.create(user=user, _name="child-genre")
    request = _drf_request(user)

    serializer = FixtureCategoryInputSerializer(
        instance=child, data={"name": "child-genre", "parent": str(parent.pk)}, context={"request": request}
    )

    assert serializer.is_valid(raise_exception=True)
    assert serializer.validated_data["parent"] == parent
