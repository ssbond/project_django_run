from django.db import models
from django.db.models import ForeignKey, CharField, TextField
from django.contrib.auth.models import User

# Create your models here.
class Run(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = TextField()