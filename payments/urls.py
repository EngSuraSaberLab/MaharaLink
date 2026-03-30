from django.urls import path
from . import views

urlpatterns = [
    path(
        "checkout/<slug:slug>/",
        views.create_checkout_session,
        name="create_checkout_session"
    ),

    path(
        "success/<slug:slug>/",
        views.payment_success,
        name="payment_success"
    ),
    path(
    "webhook/",
    views.stripe_webhook,
    name="stripe_webhook"
    ),
]