import json

import pytest
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    MethodNotAllowed,
    NotAcceptable,
    NotFound,
    PermissionDenied,
    Throttled,
)

from the_music_tree_api_kit.view.error.ApiErrorCode import ApiErrorCodeNumeric
from the_music_tree_api_kit.view.error.ErrorResponse import ErrorResponse


def _body(response):
    return json.loads(response.content)


def test_drf_not_found_maps_to_404_and_keeps_detail():
    response = ErrorResponse.handle_exception(NotFound("Track abc is not in this playlist."))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    body = _body(response)
    assert body["code"] == ApiErrorCodeNumeric.RESOURCE_NOT_FOUND
    assert body["details"] == {"message": "Track abc is not in this playlist.", "code": "not_found"}


def test_django_http404_unchanged():
    response = ErrorResponse.handle_exception(Http404("Genre missing"))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert _body(response)["details"] == {"message": "Genre missing", "code": "not_found"}


@pytest.mark.parametrize(
    ("exception", "expected_status", "expected_api_code"),
    [
        (PermissionDenied(), status.HTTP_403_FORBIDDEN, ApiErrorCodeNumeric.AUTH_INSUFFICIENT_PERMISSIONS),
        (
            MethodNotAllowed("PATCH"),
            status.HTTP_405_METHOD_NOT_ALLOWED,
            ApiErrorCodeNumeric.VALIDATION_METHOD_NOT_ALLOWED,
        ),
    ],
)
def test_dedicated_handlers_take_precedence_over_fallback(exception, expected_status, expected_api_code):
    response = ErrorResponse.handle_exception(exception)

    assert response.status_code == expected_status
    assert _body(response)["code"] == expected_api_code


@pytest.mark.parametrize(
    ("exception", "expected_status", "expected_code"),
    [
        (Throttled(wait=5), status.HTTP_429_TOO_MANY_REQUESTS, "throttled"),
        (NotAcceptable(), status.HTTP_406_NOT_ACCEPTABLE, "not_acceptable"),
    ],
)
def test_unhandled_drf_exceptions_keep_their_status(exception, expected_status, expected_code):
    response = ErrorResponse.handle_exception(exception)

    assert response.status_code == expected_status
    body = _body(response)
    assert body["code"] == ApiErrorCodeNumeric.BUSINESS_INVALID_OPERATION
    assert body["details"] == {"message": str(exception.detail), "code": expected_code}


def test_custom_api_exception_maps_to_matching_api_code():
    class Conflict(APIException):
        status_code = status.HTTP_409_CONFLICT
        default_detail = "Already there."
        default_code = "conflict"

    response = ErrorResponse.handle_exception(Conflict())

    assert response.status_code == status.HTTP_409_CONFLICT
    body = _body(response)
    assert body["code"] == ApiErrorCodeNumeric.RESOURCE_ALREADY_EXISTS
    assert body["details"] == {"message": "Already there.", "code": "conflict"}


def test_non_api_exception_still_500():
    response = ErrorResponse.handle_exception(RuntimeError("boom"))

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert _body(response)["details"]["code"] == "internal_error"
