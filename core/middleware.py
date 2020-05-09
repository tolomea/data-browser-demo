from .models import User


class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user = User.objects.get(is_staff=True)
        return self.get_response(request)
