import logging

from django.core.exceptions import DisallowedHost
from django.http import HttpRequest

from the_music_tree_api_kit.view.error.ErrorResponse import ErrorResponse


class HostValidationMiddleware:
    """Converts Django's DisallowedHost into the app's standard JSON error response.

    Relies solely on HttpRequest.get_host(), which already validates the request's
    Host header against settings.ALLOWED_HOSTS (port-stripped, wildcard-aware) and
    raises DisallowedHost itself. Do not add a second manual comparison against
    ALLOWED_HOSTS here: an earlier version did, comparing the full "host:port"
    string without stripping the port, which required every ALLOWED_HOSTS entry to
    be duplicated with and without its port to pass both checks.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger("exceptions")

    def __call__(self, request: HttpRequest):
        try:
            request.get_host()
        except DisallowedHost as exc:
            self.logger.error("%s: %s", type(exc).__name__, exc)
            return ErrorResponse.handle_exception(exc)
        return self.get_response(request)
