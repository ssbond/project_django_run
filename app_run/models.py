from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import TextField, PositiveSmallIntegerField, FloatField
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
    distance = models.FloatField(null=True,blank=True, default=None)
    class Meta:
        verbose_name = 'Забег'
        verbose_name_plural = 'Забеги'

class AthleteInfo(models.Model):
    goals = TextField(
        max_length=1500,
        verbose_name='Коротко о себе',
        default=None,
        null=True,
    )
    weight = PositiveSmallIntegerField(
        verbose_name='Вес',
        validators=[MaxValueValidator(899), MinValueValidator(1)],
        default=None,
        null=True,
    )
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    class Meta:
        verbose_name = 'Информация об атлете'
        verbose_name_plural = 'Информация об атлетах'

class Challenge(models.Model):
    full_name = models.CharField(max_length=100, verbose_name="Название челленджа")
    athlete = models.ForeignKey(User, on_delete=models.CASCADE, related_name='challenges')
    # date = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = 'Челлендж'
        verbose_name_plural = 'Челленджи'

    def __str__(self):
        return self.full_name

class Position(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE, related_name='challenges')
    latitude = models.DecimalField(
        max_digits=9,  # Всего цифр (включая после запятой)
        decimal_places=4,  # Именно 4 знака после запятой
        validators=[
            MinValueValidator(-90),
            MaxValueValidator(90)
        ]
    )
    longitude = models.DecimalField(
        max_digits=9,  # Всего цифр (включая после запятой)
        decimal_places=4,  # Именно 4 знака после запятой
        validators=[
            MinValueValidator(-180),
            MaxValueValidator(180)
        ]
    )

    # date = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = 'Местоположение'
        verbose_name_plural = 'Местоположения'

class CollectibleItem(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название артефакта")
    uid = models.CharField(max_length=100, verbose_name="Уникальный идентификатор", unique=True)
    latitude = models.DecimalField(
        max_digits=9,  # Всего цифр (включая после запятой)
        decimal_places=4,  # Именно 4 знака после запятой
        validators=[
            MinValueValidator(-90),
            MaxValueValidator(90)
        ]
    )
    longitude = models.DecimalField(
        max_digits=9,  # Всего цифр (включая после запятой)
        decimal_places=4,  # Именно 4 знака после запятой
        validators=[
            MinValueValidator(-180),
            MaxValueValidator(180)
        ]
    )
    picture = models.URLField(verbose_name="Ссылка на изображение")
    value = models.IntegerField(verbose_name="Крутизна артефакта")

    class Meta:
        verbose_name = 'Коллекционный артефакт'
        verbose_name_plural = 'Коллекционные артефакты'