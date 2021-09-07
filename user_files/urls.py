from os import name
from django.urls import path
from . import views

urlpatterns = [
    path('files', views.files, name='index'),
    path('login', views.login, name='login'),
]