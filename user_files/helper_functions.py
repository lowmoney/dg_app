import boto3
from typing import List
from .models import UserFiles, User
from secrets import token_urlsafe
from os.path import join, exists
from os import remove, getenv

# Helpful constants
SECRET = getenv('SPACE_SECRET', None)
ACCESS_KEY = getenv('SPACE_KEY', None)
CDN_URL = 'https://content.hendry.app'
BUCKET = getenv('SPACE_BUCKET', None)
CDN_ENDPOINT = getenv('SPACE_CDN_ENDPOINT', None)


def upload_files(files:List, user:User) -> bool:
    uploaded = []
    deleted = []

    try:
        for file in files:
            file_name = '{}.{}'.format(token_urlsafe(6), file.name.split('.')[1])

            with open(join('media',file_name), 'wb') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            f = open(join('media',file_name), 'rb')


            session = boto3.session.Session()
            client = session.client('s3', region_name='sfo3', endpoint_url='https://sfo3.digitaloceanspaces.com', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET)
            client.put_object(Bucket=BUCKET,
                    Key='dg-app/{}'.format(file_name),
                    Body=f,
                    ACL='private',
                    )
            f.close()

            user_file:UserFiles = UserFiles.objects.create(pub_id = file_name, user = user)
            user_file.save()

            uploaded.append(file_name)

            try:
                if exists(join('media',file_name)):
                    remove(join('media',file_name))
                    deleted.append(file_name)
            except Exception as e:
                print(e)
                pass
    except Exception as e:
        print('internal server error, something must be wrong with the credentials\n{}'.format(e))

    return True if len(uploaded) == len(deleted) and len(uploaded) != 0 and len(deleted) != 0 else False


'''
    Given the User object, finds all the files that belongs to the user and returns the urls for the files to be served
    If the expire kwarg is not given the url will expire in 5min
'''
def get_user_files(user:User, expire=5) -> List:
    urls = []

    try:
        session = boto3.session.Session()
        client = session.client('s3', region_name='sfo3', endpoint_url='https://sfo3.digitaloceanspaces.com', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET)

        files = UserFiles.objects.filter(user = user)

        for file in files:
            public_url = client.generate_presigned_url(ClientMethod='get_object', Params={'Bucket':BUCKET,'Key':'dg-app/{}'.format(file.pub_id)}, ExpiresIn=expire*60)
            urls.append(public_url)

    except Exception as e:
        print('internal server error, something must be wrong with the credentials\n{}'.format(e))

    return urls