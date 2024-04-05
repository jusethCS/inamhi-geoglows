from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    institution = models.CharField(max_length=100)
    position = models.CharField(max_length=100)

class UserActivity(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date = models.DateField()
    activity = models.CharField(max_length=100)