from rest_framework.pagination import PageNumberPagination


class Pagination(PageNumberPagination):
    """Кастомная пагинация с лимитом."""

    page_size_query_param = 'limit'
    max_page_size = 50
    page_size = 6
