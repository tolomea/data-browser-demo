import hashlib
import time

from django.contrib.auth.models import Group
from django.core.cache import cache
from django.http import HttpResponse

from . import fixtures


class RateLimitMiddleware:
    """Rate limit requests by /16 network block."""

    REQUESTS_PER_MINUTE = 20
    EXCLUDED_PATHS = ["/static/", "/robots.txt"]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip rate limiting for excluded paths
        for excluded_path in self.EXCLUDED_PATHS:
            if request.path.startswith(excluded_path):
                return self.get_response(request)

        # Get /16 network from IP
        ip = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
        if not ip:
            ip = request.META.get("REMOTE_ADDR", "")

        # Extract /16 network (first two octets)
        try:
            octets = ip.split(".")
            network = f"{octets[0]}.{octets[1]}"
        except (IndexError, AttributeError):
            # Invalid IP, allow request
            return self.get_response(request)

        # Check rate limit using cache
        cache_key = f"ratelimit:{network}"
        current_minute = int(time.time() / 60)
        cache_key_with_minute = f"{cache_key}:{current_minute}"

        request_count = cache.get(cache_key_with_minute, 0)

        if request_count >= self.REQUESTS_PER_MINUTE:
            return HttpResponse(
                f"Rate limit exceeded for network {network}.0.0/16. "
                f"Limit: {self.REQUESTS_PER_MINUTE} requests per minute.",
                status=429,
            )

        # Increment counter
        cache.set(cache_key_with_minute, request_count + 1, 60)

        return self.get_response(request)


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

        if request.path.startswith("/data-browser/"):
            # Data browser: get_or_create user for legitimate demo users
            user, created = fixtures.get_or_create_admin_user(username)
            if created:
                user.groups.set(Group.objects.all())
                fixtures.create_views(user)
            request.user = user
        elif request.path.startswith("/admin/"):
            # Admin honeypot: block new users, allow existing users
            try:
                user = fixtures.models.User.objects.get(username=username)
                request.user = user
            except fixtures.models.User.DoesNotExist:
                return HttpResponse(
                    "Access denied. Please visit the data browser first.", status=403
                )
        else:
            # Other paths (static, robots.txt, etc.): no user needed
            pass

        return self.get_response(request)
