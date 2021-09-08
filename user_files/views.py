from django.db.models import fields
from django.http import response
from django.shortcuts import render, redirect
import os, boto3
from secrets import token_urlsafe
from django.core.exceptions import ObjectDoesNotExist
from .models import UserFiles, User, CustomeSessions

# Create your views here.


# Helpful constants
SECRET = '4RWQieV2WnIC316weoRenRrxkStqmGgYVgnk7udewyc'
ACCESS_KEY = 'E7GOYNUZVENL7DMQ5ERW'
CDN_URL = 'https://content.hendry.app'
CDN_ENDPOINT = ''



def files(request):
    SESSION = request.COOKIES.get('session')
    LOGGED_IN = False
    USER = None


    if SESSION is not None:
        try:
            USER = CustomeSessions.objects.get(session_key = SESSION)
            USER = USER.user
            LOGGED_IN = True
        except Exception as e:
            print('not found')
            print(e)
            pass

    if request.method == 'POST' and LOGGED_IN is True:
        file = request.FILES.get('file')

        file_name = token_urlsafe(6)
        file_type = file.name.split('.')[1]

        with open('media/{}.{}'.format(file_name, file_type), 'wb') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        f = open('media/{}.{}'.format(file_name, file_type), 'rb')


        session = boto3.session.Session()
        client = session.client('s3', region_name='sfo3', endpoint_url='https://sfo3.digitaloceanspaces.com', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET)
        client.put_object(Bucket='example-work-blob',
                  Key='dg-app/{}.{}'.format(file_name, file_type),
                  Body=f,
                  ACL='private',
                )
        f.close()

        public_url = client.generate_presigned_url(ClientMethod='get_object', Params={'Bucket':'example-work-blob','Key':'{}.{}'.format(file_name, file_type)}, ExpiresIn=10)


        user_file = UserFiles()
        user_file.pub_id = file_name
        user_file.file_type = file_type
        user_file.pub_url = public_url
        user_file.user = USER
        user_file.save()

        try:
            if os.path.exists('media/{}.{}'.format(file_name, file_type)):
                os.remove('media/{}.{}'.format(file_name, file_type))
        except:
            pass

        return render(request, 'user_files/index.html',{'uploaded':user_file})
    elif request.method == 'GET' and LOGGED_IN is True:
        session = boto3.session.Session()
        client = session.client('s3', region_name='sfo3', endpoint_url='https://sfo3.digitaloceanspaces.com', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET)

        files = UserFiles.objects.filter(user = USER)
        public_urls = []

        for file in files:
            public_url = client.generate_presigned_url(ClientMethod='get_object', Params={'Bucket':'example-work-blob','Key':'dg-app/{}.{}'.format(file.pub_id, file.file_type)}, ExpiresIn=120)
            public_urls.append(public_url)


        return render(request, 'user_files/index.html', {'urls':public_urls})
    else:
        return redirect('/')

def login(request):
    err = False
    succ = False
    SESSION = request.COOKIES.get('session')
    LOGGED_IN = False


    if SESSION is not None:
        try:
            USER = CustomeSessions.objects.get(session_key = SESSION)
            LOGGED_IN = True
        except:
            pass

    
    response = render(request, 'user_files/login.html', {'err':err, 'succ':succ})

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password is not None:
            try:
                user = User.objects.get(username = username)
                if password == user.password:
                    session = CustomeSessions()
                    session.session_key = token_urlsafe(32)
                    session.user = user

                    session.save()
                    response = redirect('/files')
                    response.set_cookie('session', session.session_key)
                else:
                    err = True
            except ObjectDoesNotExist:

                user = User()
                session = CustomeSessions()

                user.username = username
                user.password = password

                session.session_key = token_urlsafe(32)
                session.user = user

                user.save()
                session.save()

                succ = True
                response = redirect('/files')
                response.set_cookie('session',session)
            except:
                user = User.objects.get(username = username)
                session = CustomeSessions.objects.get(user = user)
                session.delete()
                if password == user.password:
                    session = CustomeSessions()
                    session.session_key = token_urlsafe(32)
                    session.user = user

                    session.save()
                    response = redirect('/files')
                    response.set_cookie('session', session.session_key)



        else:
            err = True

        return response
    elif request.method == 'GET' and LOGGED_IN == True:
        return redirect('/files')
    else:
        return response

def log_off(request):
    session = request.COOKIES.get('session')
    try:
        session = CustomeSessions.objects.get(session_key = session)
        session.delete()
    except:
        pass
    response = redirect('/')
    response.delete_cookie('session')

    return response