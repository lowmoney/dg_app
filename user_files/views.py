from django.shortcuts import render, redirect
from secrets import token_urlsafe
from passlib.hash import argon2

from .models import User, Sessions

from .helper_functions import upload_files, get_user_files
from .helper_decorators import isLoggedIn

# Create your views here.
def index(request):
    return render(request, 'user_files/index.html')


@isLoggedIn
def files(request):
    session = request.COOKIES.get('session')
    session = Sessions.objects.get(session_key = session)
    user = session.user

    context = {}


    if request.method == 'POST':
        files = request.FILES.getlist('files')
        if upload_files(files, user):
            context['uploaded_files'] = True
        else:
            context['error_uploaded_files'] = True


    context['urls'] = get_user_files(user)

    return render(request, 'user_files/files.html', context)



def register(request):
    response = render(request, 'user_files/register.html')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user:User = User.objects.create(username = username, password = argon2.hash(password))
            user.save()
            response = redirect('/login')
        except:
            response = render(request, 'user_files/register.html', {'err':'issue with the credentials'})
    
    return response


def login(request):

    response = render(request, 'user_files/login.html')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user:User = User.objects.get(username = username)
            if argon2.verify(password, user.password):
                session , __ = Sessions.objects.update_or_create(user = user, defaults = {'session_key' : token_urlsafe(32)})
                session.save()

                response = redirect('/files')
                response.set_cookie('session', session.session_key)
        except Exception as e:
            print(e)
            pass

    return response

def log_off(request):
    session = request.COOKIES.get('session')
    try:
        session = Sessions.objects.get(session_key = session)
        session.delete()
    except:
        pass

    response = redirect('/')
    response.delete_cookie('session')

    return response