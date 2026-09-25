from typing import Any


def get_request_owner(request: Any) -> Any:
    """
    The user whose private rows this request reads and writes. `AppModelViewSet` resolves it into
    `request.owner` (`None` meaning ownerless, shared rows); requests that never went through a
    viewset fall back to the caller.
    """
    return getattr(request, "owner", request.user)
