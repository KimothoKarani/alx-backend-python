# messaging_app/chats/pagination.py

from rest_framework.pagination import PageNumberPagination

class StandardPagination(PageNumberPagination):
    """
    Custom pagination class for DRF.
    Sets default page size and allows client to override.
    """
    page_size = 20 # Default page size
    page_size_query_param = 'page_size' # Allows client to specify page size, e.g., ?page_size=50
    max_page_size = 100 # Maximum page size a client can request