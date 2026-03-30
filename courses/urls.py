from django.urls import path
from . import views

urlpatterns = [
    path('', views.homePage,name='homePage'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/<slug:slug>/', views.course_detail, name='course_detail'),
    path('video/<slug:slug>/', views.course_video, name='course_video'),
]
