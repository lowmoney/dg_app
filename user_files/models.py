from django.db import models

# Create your models here.
class UserFiles(models.Model):
    pub_id = models.CharField(max_length=6, unique=True, null=False, blank=False)
    file_type = models.CharField(max_length=16, null=False, blank=False, default='jpg')
    pub_url = models.CharField(max_length=128, null=True, blank=True) 