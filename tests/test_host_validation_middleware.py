from django.http import HttpResponse
from django.test import RequestFactory, override_settings

from the_music_tree_api_kit.view.middleware.HostValidationMiddleware import HostValidationMiddleware


def _passthrough(request):
    return HttpResponse("ok")


@override_settings(ALLOWED_HOSTS=["example.com", "localhost"])
def test_allowed_host_passes_through():
    request = RequestFactory().get("/", HTTP_HOST="example.com")
    response = HostValidationMiddleware(_passthrough)(request)
    assert response.status_code == 200


@override_settings(ALLOWED_HOSTS=["example.com", "localhost"])
def test_bare_localhost_allows_healthcheck_host_with_port():
    request = RequestFactory().get("/", HTTP_HOST="localhost:8000")
    response = HostValidationMiddleware(_passthrough)(request)
    assert response.status_code == 200


@override_settings(ALLOWED_HOSTS=["example.com"])
def test_disallowed_host_returns_error_response():
    request = RequestFactory().get("/", HTTP_HOST="evil.com")
    response = HostValidationMiddleware(_passthrough)(request)
    assert response.status_code == 400
