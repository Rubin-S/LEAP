import logging
from django.http import Http404
from django.shortcuts import render

logger = logging.getLogger(__name__)

class CustomErrorHandlingMiddleware:
    """
    Middleware to render friendly error pages and log exceptions.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):

        if isinstance(exception, Http404):
            logger.warning("404 Not Found: %s", request.path)
            return render(request, '404.html', {'status_code': 404, 'request_path': request.path}, status=404)

        logger.exception("Unhandled exception at %s", request.path)
        return render(request, '500.html', {'status_code': 500, 'request_path': request.path}, status=500)
