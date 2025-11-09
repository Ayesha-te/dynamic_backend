import logging
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    
    if response is None:
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return Response(
            {"error": "An unexpected error occurred", "detail": str(exc)},
            status=500
        )
    
    if response.status_code >= 500:
        logger.error(f"Server error: {response.data}", exc_info=True)
    
    return response
