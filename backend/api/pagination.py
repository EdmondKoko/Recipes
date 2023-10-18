from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Пагинация с номерами страниц."""
    page_size_query_param = 'limit'
