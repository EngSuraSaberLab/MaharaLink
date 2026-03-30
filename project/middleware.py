from django.conf import settings
from django.utils import translation


class DefaultArabicLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        has_language_cookie = bool(request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME))

        if not has_language_cookie:
            translation.activate("ar")
            request.LANGUAGE_CODE = "ar"

        response = self.get_response(request)

        if not has_language_cookie:
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, "ar")

        return response
