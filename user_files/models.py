from django.db import models

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=20, unique=True)

class UserFiles(models.Model):
    pub_id = models.CharField(max_length=6, unique=True, null=False, blank=False)
    file_type = models.CharField(max_length=16, null=False, blank=False, default='jpg')
    pub_url = models.CharField(max_length=128, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class CustomeSessions(models.Model):
    session_key = models.CharField(max_length=32, unique=True, blank=True, null=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, unique=True)