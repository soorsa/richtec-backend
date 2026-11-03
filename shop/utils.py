from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    # Set the name of the query parameter you want to use
    page_size_query_param = 'page_size' 
    
    def paginate_queryset(self, queryset, request, view=None):
        # Check if the client explicitly asked to bypass pagination
        if request.query_params.get('paginate') == 'false':
            return None  # Returning None tells DRF to skip pagination entirely
            
        return super().paginate_queryset(queryset, request, view=view)