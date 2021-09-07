from os import name
from django.urls import path
from . import views

urlpatterns = [
    path('files', views.files, name='index'),
    path('', views.login, name='login'),
    path('log_off', views.log_off, name='log_off'),
]