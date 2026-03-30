from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.blogPage, name="blogPage"),
    path("<slug:slug>/", views.blogDetail, name="blogDetail"),
]