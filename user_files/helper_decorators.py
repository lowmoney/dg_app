from .models import Sessions
from django.shortcuts import redirect

def isLoggedIn(func):
    def wrapper(request, *args, **kwargs):
        session = request.COOKIES.get('session')
        try:
            session = Sessions.objects.get(session_key = session)
            return func(request)
        except:
            return redirect('/log_off')

    return wrapper