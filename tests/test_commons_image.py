import pytest
from django.db import IntegrityError, transaction

from tests.fixture_app.models import FixtureImaged
from the_music_tree_api_kit.commons_image.CommonsImageSerializer import CommonsImageSerializer
from the_music_tree_api_kit.commons_image.helpers import commons_image_kwargs, commons_image_representation
from the_music_tree_api_kit.commons_image.validation import IMAGE_URL_LEN_MAX, validate_commons_image
from the_music_tree_api_kit.exception.validation.app.AppValidationException import AppValidationException

VALID = {
    "url": "https://upload.wikimedia.org/a.jpg",
    "page_url": "https://commons.wikimedia.org/wiki/File:A.jpg",
    "author": "Jane Doe",
    "license": "CC BY-SA 4.0",
    "license_url": "https://creativecommons.org/licenses/by-sa/4.0",
}


def _https(length_bytes: int) -> str:
    prefix = "https://x/"
    return prefix + "a" * (length_bytes - len(prefix))


def test_valid_image():
    assert validate_commons_image(VALID) is None


def test_null_author_and_license_url_are_valid():
    assert validate_commons_image({**VALID, "author": None, "license_url": None}) is None


def test_http_license_url_is_valid():
    assert validate_commons_image({**VALID, "license_url": "http://creativecommons.org/licenses/by/3.0"}) is None


@pytest.mark.parametrize("value", ["x", [], 3])
def test_non_object_rejected(value):
    assert validate_commons_image(value) == "image must be an object"


@pytest.mark.parametrize("key", ["url", "page_url"])
@pytest.mark.parametrize("value", ["http://x/a.jpg", "", None, 3])
def test_non_https_url_rejected(key, value):
    assert validate_commons_image({**VALID, key: value}) == (
        f"image {key} must be an https URL of at most {IMAGE_URL_LEN_MAX} bytes"
    )


def test_url_length_is_measured_in_bytes():
    assert validate_commons_image({**VALID, "url": _https(IMAGE_URL_LEN_MAX)}) is None
    assert validate_commons_image({**VALID, "url": _https(IMAGE_URL_LEN_MAX) + "a"}) is not None
    # 1024 two-byte characters fit by length but not by bytes.
    assert validate_commons_image({**VALID, "url": "https://x/" + "é" * 1024}) is not None


@pytest.mark.parametrize("value", ["", None])
def test_empty_license_rejected(value):
    assert validate_commons_image({**VALID, "license": value}) == "image license must be a non-empty string"


def test_empty_author_rejected():
    assert validate_commons_image({**VALID, "author": ""}) == "image author must be a non-empty string"


@pytest.mark.parametrize("value", ["", "ftp://x", "creativecommons.org", _https(IMAGE_URL_LEN_MAX) + "a"])
def test_bad_license_url_rejected(value):
    assert validate_commons_image({**VALID, "license_url": value}) == (
        f"image license_url must be an http(s) URL of at most {IMAGE_URL_LEN_MAX} bytes"
    )


def test_kwargs_maps_image_and_none_clears():
    assert commons_image_kwargs(VALID) == {
        "image_url": VALID["url"],
        "image_page_url": VALID["page_url"],
        "image_author": "Jane Doe",
        "image_license": "CC BY-SA 4.0",
        "image_license_url": VALID["license_url"],
    }
    assert commons_image_kwargs(None) == dict.fromkeys(
        ["image_url", "image_page_url", "image_author", "image_license", "image_license_url"]
    )
    assert commons_image_kwargs({**VALID, "author": None})["image_author"] is None


def test_representation_round_trips():
    assert commons_image_representation(FixtureImaged(**commons_image_kwargs(VALID))) == VALID
    assert commons_image_representation(FixtureImaged()) is None


def test_serializer_accepts_valid_image():
    assert CommonsImageSerializer().run_validation(dict(VALID)) == VALID


def test_serializer_accepts_missing_optional_keys():
    data = {"url": VALID["url"], "page_url": VALID["page_url"], "license": "CC0"}
    assert CommonsImageSerializer().run_validation(data) == data


def test_serializer_null_only_when_allowed():
    assert CommonsImageSerializer(allow_null=True).run_validation(None) is None


def test_serializer_rejects_http_url():
    with pytest.raises(AppValidationException):
        CommonsImageSerializer().run_validation({**VALID, "url": "http://x/a.jpg"})


def test_serializer_rejects_missing_url():
    with pytest.raises(AppValidationException):
        CommonsImageSerializer().run_validation({k: v for k, v in VALID.items() if k != "url"})


def test_serializer_rejects_unknown_key():
    with pytest.raises(AppValidationException):
        CommonsImageSerializer().run_validation({**VALID, "extra": 1})


@pytest.mark.django_db
def test_constraint_allows_complete_and_empty(django_user_model):
    user = django_user_model.objects.create(username="u")
    FixtureImaged.objects.create(user=user, _name="a")
    FixtureImaged.objects.create(user=user, _name="b", **commons_image_kwargs({**VALID, "author": None}))


@pytest.mark.django_db
@pytest.mark.parametrize("missing", ["image_url", "image_page_url", "image_license"])
def test_constraint_rejects_partial_image(django_user_model, missing):
    user = django_user_model.objects.create(username="u")
    kwargs = commons_image_kwargs(VALID) | {missing: None}
    with pytest.raises(IntegrityError), transaction.atomic():
        FixtureImaged.objects.create(user=user, _name="a", **kwargs)


@pytest.mark.django_db
def test_constraint_rejects_orphan_author(django_user_model):
    user = django_user_model.objects.create(username="u")
    with pytest.raises(IntegrityError), transaction.atomic():
        FixtureImaged.objects.create(user=user, _name="a", image_author="Jane")
