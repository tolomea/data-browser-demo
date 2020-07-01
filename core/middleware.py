import hashlib

from django.contrib.auth.models import Group

from . import fixtures


class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        username = hashlib.md5(
            request.META.get("HTTP_X_FORWARDED_FOR", "").encode("utf-8")
        ).hexdigest()
        user, created = fixtures.get_or_create_admin_user(username)
        if created:
            user.groups.set(Group.objects.all())
            fixtures.create_views(user)
        request.user = user
        return self.get_response(request)
