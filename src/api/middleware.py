class CacheControlMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Define paths and their cache settings
        self.cache_enabled_paths = {
            '/api/get_my_chat_history/chart_image': 'max-age=600',
            '/api/get_my_chat_history/results_json': 'max-age=600',
        }

    def __call__(self, request):
        response = self.get_response(request)
        path = request.path

        # Check if the path is in the disabled list and set no-cache headers
        if path in self.cache_enabled_paths:
            response['Cache-Control'] = self.cache_enabled_paths[path]
        else:
            response['Cache-Control'] = 'no-store'
            response['Pragma'] = 'no-cache'

        headers_to_remove = [
            'X-Powered-By',
            'Server',
        ]

        # Remove the headers
        for header in headers_to_remove:
            response.headers.pop(header, None)

        return response
