"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from courses.views import media_file


urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),

    path("admin/", admin.site.urls),

    path("accounts/", include("registration.urls")),
    path("blog/", include("blog.urls")),
    path("payments/", include("payments.urls")),
    path("", include("courses.urls")),

    path("media/<path:file_path>", media_file),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
