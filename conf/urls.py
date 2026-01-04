"""conf URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path


def trigger_error(request):
    division_by_zero = 1 / 0  # noqa F841


def robots_txt(request):
    content = """User-agent: *
Disallow: /
"""
    return HttpResponse(content, content_type="text/plain")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("data-browser/", include("data_browser.urls")),
    path("sentry-debug/", trigger_error),
    path("robots.txt", robots_txt),
]
