from django.conf import settings
from rest_framework.exceptions import ParseError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .PaginatedResponseFields import PaginatedResponseFields


class AppPagination(PageNumberPagination):
    page_size: int = settings.PAGINATION_PAGE_SIZE_DEFAULT
    page_size_query_param = "page_size"
    max_page_size = settings.PAGINATION_PAGE_SIZE_MAX

    def get_page_number(self, request, paginator):
        """
        Override to return 400 Bad Request for invalid page numbers
        instead of 404 Not Found.
        """
        page_number = request.query_params.get(self.page_query_param, 1)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages
        try:
            page_number = int(page_number)
            if page_number < 1:
                raise ParseError("Invalid page.")
        except TypeError, ValueError:
            raise ParseError("Invalid page.")

        return page_number

    def get_page_size(self, request):
        """
        Reject a non-integer or < 1 `page_size` with 400 (DRF would otherwise
        fall back silently or, for 0, disable pagination), and cap it at the max.
        """
        if request is None or self.page_size_query_param not in request.query_params:
            return self.page_size

        try:
            page_size = int(request.query_params[self.page_size_query_param])
        except TypeError, ValueError:
            raise ParseError("Invalid page size.")
        if page_size < 1:
            raise ParseError("Invalid page size.")

        return min(page_size, self.max_page_size) if self.max_page_size else page_size

    def get_paginated_response(self, data):
        paginator = self.page.paginator
        count = paginator.count
        return Response(
            {
                PaginatedResponseFields.OVERALL_TOTAL: count,
                PaginatedResponseFields.NEXT: self.get_next_link(),
                PaginatedResponseFields.PREVIOUS: self.get_previous_link(),
                PaginatedResponseFields.RESULTS: data,
                PaginatedResponseFields.PAGE: self.page.number,
                PaginatedResponseFields.PAGE_SIZE: paginator.per_page,
                PaginatedResponseFields.TOTAL_PAGES: paginator.num_pages if count > 0 else 0,
            }
        )

    def get_paginated_response_schema(self, schema):
        integer = {"type": "integer"}
        link = {"type": "string", "nullable": True, "format": "uri"}
        return {
            "type": "object",
            "required": [
                PaginatedResponseFields.OVERALL_TOTAL,
                PaginatedResponseFields.NEXT,
                PaginatedResponseFields.PREVIOUS,
                PaginatedResponseFields.RESULTS,
                PaginatedResponseFields.PAGE,
                PaginatedResponseFields.PAGE_SIZE,
                PaginatedResponseFields.TOTAL_PAGES,
            ],
            "properties": {
                PaginatedResponseFields.OVERALL_TOTAL: integer,
                PaginatedResponseFields.NEXT: link,
                PaginatedResponseFields.PREVIOUS: link,
                PaginatedResponseFields.RESULTS: schema,
                PaginatedResponseFields.PAGE: integer,
                PaginatedResponseFields.PAGE_SIZE: integer,
                PaginatedResponseFields.TOTAL_PAGES: integer,
            },
        }

    @property
    def count(self) -> int:
        """Get total count of items across all pages with null safety"""
        if not hasattr(self, "page") or self.page is None:
            return 0
        if not hasattr(self.page, "paginator"):
            return 0
        return getattr(self.page.paginator, "count", 0)
