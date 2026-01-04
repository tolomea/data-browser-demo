import hashlib

from django.contrib.auth.models import Group
from django.http import HttpResponse

from . import fixtures


class BlockBotsMiddleware:
    """Block requests from known crawlers/bots."""

    BOT_USER_AGENTS = [
        "bot",
        "crawl",
        "spider",
        "scrape",
        "slurp",
        "yahoo",
        "googlebot",
        "bingbot",
        "amazonbot",
        "facebookexternalhit",
        "twitterbot",
        "whatsapp",
        "linkedinbot",
        "baiduspider",
        "yandex",
        "duckduckbot",
        "applebot",
        "semrush",
        "ahrefs",
        "mj12bot",
        "dotbot",
        "rogerbot",
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Allow bots to read robots.txt
        if request.path == "/robots.txt":
            return self.get_response(request)

        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()

        # Block known bot user agents
        for bot_pattern in self.BOT_USER_AGENTS:
            if bot_pattern in user_agent:
                return HttpResponse(
                    "Bots are not allowed. Please check /robots.txt", status=403
                )

        return self.get_response(request)


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
