from django.shortcuts import render
import os, boto3
from secrets import token_urlsafe

from .models import UserFiles

# Create your views here.
SECRET = '4RWQieV2WnIC316weoRenRrxkStqmGgYVgnk7udewyc'
ACCESS_KEY = 'E7GOYNUZVENL7DMQ5ERW'
CDN_URL = 'https://content.hendry.app'

def index(request):
    if request.method == 'POST':
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
        user_file.save()

        try:
            if os.path.exists('media/{}.{}'.format(file_name, file_type)):
                os.remove('media/{}.{}'.format(file_name, file_type))
        except:
            pass

        return render(request, 'user_files/index.html',{'uploaded':user_file})
    else:
        return render(request, 'user_files/index.html')