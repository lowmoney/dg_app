from os import name
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('files', views.files, name='files'),
    path('login', views.login, name='login'),
    path('register', views.register, name='login'),
    path('log_off', views.log_off, name='log_off'),
]