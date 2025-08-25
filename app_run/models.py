from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import TextField, PositiveSmallIntegerField
from django.contrib.auth.models import User

# Create your models here.
class Run(models.Model):
    STATUS_CHOICES = [
        ('init', 'Забег инициализирован'),
        ('in_progress', 'Забег начат'),
        ('finished', 'Забег закончен'),
    ]
    created_at = models.DateTimeField(auto_now_add=True)
    athlete = models.ForeignKey(User, on_delete=models.CASCADE, related_name='runs')
    comment = TextField()
    status = models.CharField(
        max_length=30,
        choices= STATUS_CHOICES,
        default='init'
    )



class AthleteInfo(models.Model):
    goals = TextField(
        max_length=1500,
        verbose_name='Коротко о себе',
        default=None,
        null=True,
    )
    weight = PositiveSmallIntegerField(
        verbose_name='Вес',
        validators=[MaxValueValidator(900)],
        default=None,
        null=True,
    )
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)