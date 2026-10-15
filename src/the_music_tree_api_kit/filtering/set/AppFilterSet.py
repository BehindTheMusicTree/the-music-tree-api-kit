from django_filters import FilterSet

from the_music_tree_api_kit.base.BaseQuerySet import BaseQuerySet
from the_music_tree_api_kit.exception.validation.app.AppValidationException import AppValidationException
from the_music_tree_api_kit.exception.validation.FieldValidationErrorCode import FieldValidationErrorCode
from the_music_tree_api_kit.utils import data_transformer

PAGINATION_PARAMS = frozenset({"page", "page_size"})


class AppFilterSet(FilterSet):
    # Snake_case names: incoming params are snake-cased before comparison, so camelCase clients match too
    allowed_non_filter_params = PAGINATION_PARAMS
    strict = False

    @property
    def qs(self):
        valid_filters = set(self.filters.keys())
        invalid_filters = []

        for param in self.data:
            snake_param = data_transformer.to_snake_case(param)
            if param not in valid_filters and snake_param not in self.allowed_non_filter_params:
                invalid_filters.append(data_transformer.to_camel_case(param))

        if invalid_filters:
            if len(invalid_filters) == 1:
                raise AppValidationException(
                    field_name=f"{invalid_filters[0]}",
                    message="Invalid filter detected",
                    field_validation_error_code=FieldValidationErrorCode.INVALID_FILTER,
                )

            raise AppValidationException(
                field_name=f"{', '.join(sorted(invalid_filters))}",
                message="Invalid filters detected",
                field_validation_error_code=FieldValidationErrorCode.INVALID_FILTERS,
            )

        queryset = super().qs
        if not isinstance(queryset, BaseQuerySet):
            # Wrap without losing the filters/query already applied by super().qs
            queryset = BaseQuerySet(queryset.model, query=queryset.query, using=queryset.db)
        return queryset
