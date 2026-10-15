import pytest
from django.http import QueryDict

from tests.fixture_app.models import FixtureItem
from the_music_tree_api_kit.exception.validation.app.AppValidationException import AppValidationException
from the_music_tree_api_kit.filtering.set.AppFilterSet import AppFilterSet


class _ItemFilterSet(AppFilterSet):
    allowed_non_filter_params = AppFilterSet.allowed_non_filter_params | {"with_total"}

    class Meta:
        model = FixtureItem
        fields = []


def _qs(query):
    return _ItemFilterSet(data=QueryDict(query), queryset=FixtureItem.objects.all()).qs


@pytest.mark.django_db
@pytest.mark.parametrize("query", ["page=1", "page_size=5", "pageSize=5", "with_total=false", "withTotal=false"])
def test_non_filter_params_are_accepted_in_either_case(query):
    _qs(query)


@pytest.mark.django_db
def test_unknown_param_is_rejected():
    with pytest.raises(AppValidationException):
        _qs("bogus=1")
