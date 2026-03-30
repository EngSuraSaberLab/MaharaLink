from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.CustomLoginView.as_view(), name="login"),

    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "password_change/",
        views.CustomPasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="registration/password_change_done.html"
        ),
        name="password_change_done",
    ),

    path("signup/", views.signup_view, name="signup"),

]
