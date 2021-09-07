from django.db.models import fields
from django.shortcuts import render, redirect
import os, boto3
from secrets import token_urlsafe

from .models import UserFiles, User

# Create your views here.
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
            USER = User.objects.get(session = SESSION)
            LOGGED_IN = True
        except:
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
                  Key='{}.{}'.format(file_name, file_type),
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
            public_url = client.generate_presigned_url(ClientMethod='get_object', Params={'Bucket':'example-work-blob','Key':'{}.{}'.format(file.pub_id, file.file_type)}, ExpiresIn=120)
            public_urls.append(public_url)
        return render(request, 'user_files/index.html', {'urls':public_urls})
    else:
        return redirect('/login')

def login(request):
    err = False
    succ = False
    response = render(request, 'user_files/login.html', {'err':err, 'succ':succ})
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username and password is not None:
            try:
                user = User.objects.get(username = username)
                if password == user.password:
                    session = token_urlsafe(32)
                    user.session = session
                    response.set_cookie('session', session)
                else:
                    err = True
            except:
                user = User()
                user.username = username
                user.password = password
                user.session = token_urlsafe(32)
                user.save()
                succ = True
                response.set_cookie('session',user.session)


        else:
            err = True

        return response
    else:
        return response