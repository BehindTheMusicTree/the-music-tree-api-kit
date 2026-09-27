from django.db.models import QuerySet


class EagerLoadingMixin:
    """
    Lets a serializer declare the joins, prefetches and annotations its own fields read, so
    `AppModelViewSet` loads them up front instead of issuing queries per serialized row.

    `prefix` is the relation path from the queryset's model to this serializer's instance, which
    lets a parent serializer compose a nested one's needs next to the field that nests it:

        @classmethod
        def setup_queryset(cls, queryset, prefix=""):
            queryset = queryset.select_related(f"{prefix}criteria")
            return CriteriaSerializer.setup_queryset(queryset, prefix=f"{prefix}criteria__")

    Detailed responses re-read the instance through `setup_queryset`, so attributes or annotations an
    overridden `get_object` put on the instance are not seen by an opted-in serializer.
    """

    @classmethod
    def setup_queryset(cls, queryset: QuerySet, prefix: str = "") -> QuerySet:  # noqa: ARG003 - overrides use it
        return queryset
