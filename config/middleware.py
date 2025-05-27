import uuid

class VisitorIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        visitor_id = request.COOKIES.get('visitor_id')
        if not visitor_id:
            visitor_id = str(uuid.uuid4())
            request.new_visitor_id = visitor_id

        request.visitor_id = visitor_id or request.new_visitor_id
        response = self.get_response(request)

        if hasattr(request, 'new_visitor_id'):
            response.set_cookie('visitor_id', request.new_visitor_id, max_age=60*60*24*365)

        return response
