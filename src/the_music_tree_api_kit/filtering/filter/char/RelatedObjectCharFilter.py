from django.core.exceptions import ImproperlyConfigured
from django.db.models import Exists, OuterRef, Q, QuerySet
from django.db.models.constants import LOOKUP_SEP

from the_music_tree_api_kit.filtering.filter.char.EmptiableCharFilter import EmptiableCharFilter


class RelatedObjectCharFilter(EmptiableCharFilter):
    """
    A filter that handles filtering by a primary field of a related instance.
    When the filter value is empty, it returns results with no related instance.
    Never repeats a row: a many-to-many relation is matched with EXISTS. Reverse relations and nested paths are not supported.
    """

    def __init__(self, primary_field: str, lookup_expr: str = "iexact", *args, **kwargs):
        if not primary_field:
            raise ImproperlyConfigured(f"{self.__class__.__name__} requires a primary_field argument.")

        self.primary_field = primary_field
        kwargs["lookup_expr"] = lookup_expr
        super().__init__(*args, **kwargs)

    def filter(self, qs: QuerySet, value: str | None) -> QuerySet:
        if not self.field_name:
            raise ImproperlyConfigured("field_name must be set.")
        if LOOKUP_SEP in self.field_name:
            raise ImproperlyConfigured(f"{self.__class__.__name__} does not support nested paths: {self.field_name}.")

        if value is None:
            return qs

        if value == "":
            if not self.is_param_in_request():
                return qs
            return qs.filter(**{f"{self.field_name}__isnull": True})

        lookup = f"{self.primary_field}__{self.lookup_expr}"
        relation = qs.model._meta.get_field(self.field_name)
        if not relation.is_relation:
            raise ImproperlyConfigured(f"{self.field_name} is not a relation.")
        if relation.one_to_many or (relation.many_to_many and relation.auto_created):
            raise ImproperlyConfigured(f"{self.__class__.__name__} does not support reverse relations.")
        if not relation.many_to_many:
            # To-one: the join cannot repeat a row.
            return qs.filter(Q(**{f"{self.field_name}__{lookup}": value}))

        # A many-to-many join returns a row once per matching related row; EXISTS keeps one.
        through = relation.remote_field.through
        source_name = relation.m2m_field_name()
        # Not always the pk: the through foreign key may declare to_field.
        source_key = through._meta.get_field(source_name).target_field.attname
        matches = through._base_manager.filter(
            **{
                source_name: OuterRef(source_key),
                f"{relation.m2m_reverse_field_name()}__{lookup}": value,
            }
        )
        return qs.filter(Exists(matches))
