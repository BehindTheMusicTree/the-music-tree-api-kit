from typing import Any

from the_music_tree_api_kit.view.viewset.model.AppModelViewSet import AppModelViewSet


class _FakeUser:
    pass


class _FakeSerializer:
    def __init__(self, *, instance=None, data=None, partial=False, context=None):
        self._data = data or {}

    def is_valid(self, raise_exception=False):
        return True

    @property
    def validated_data(self):
        return dict(self._data)


class _RecordingManager:
    def __init__(self):
        self.create_calls: list[dict[str, Any]] = []
        self.update_calls: list[dict[str, Any]] = []
        self.delete_calls: list[dict[str, Any]] = []

    def create(self, **kwargs):
        self.create_calls.append(kwargs)
        return "created"

    def update_instance(self, instance, **kwargs):
        self.update_calls.append(kwargs)
        return "updated"

    def delete_instance(self, instance, **kwargs):
        self.delete_calls.append(kwargs)


class _FakeModel:
    objects = _RecordingManager()


class _ViewSetWithoutOverride(AppModelViewSet):
    model_class = _FakeModel
    create_serializer_class = _FakeSerializer
    update_serializer_class = _FakeSerializer

    def get_object(self):
        return "existing"


class _ViewSetWithOverride(_ViewSetWithoutOverride):
    def _get_manager_write_kwargs(self, request):
        return {"actor": "admin@example.com"}


def _make_viewset(cls):
    viewset = cls(
        model_class=_FakeModel,
        create_serializer_class=_FakeSerializer,
        update_serializer_class=_FakeSerializer,
    )
    viewset.request = type("Req", (), {"user": _FakeUser()})()
    return viewset


def test_default_manager_write_kwargs_is_empty():
    viewset = _make_viewset(_ViewSetWithoutOverride)

    viewset._create_instance(request=viewset.request, create_data={})

    assert viewset.model_class.objects.create_calls[-1] == {"user": viewset.request.user}


def test_create_update_destroy_forward_manager_write_kwargs():
    viewset = _make_viewset(_ViewSetWithOverride)
    manager = viewset.model_class.objects

    viewset._create_instance(request=viewset.request, create_data={})
    viewset._update_instance(request=viewset.request, instance="existing", update_data={})
    viewset._handle_destroy()

    assert manager.create_calls[-1]["actor"] == "admin@example.com"
    assert manager.update_calls[-1]["actor"] == "admin@example.com"
    assert manager.delete_calls[-1]["actor"] == "admin@example.com"
