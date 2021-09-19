from django.db import models

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=77, unique=True)

class UserFiles(models.Model):
    pub_id = models.CharField(max_length=16, unique=True, null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Sessions(models.Model):
    session_key = models.CharField(max_length=43, unique=True, blank=True, null=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, unique=True)