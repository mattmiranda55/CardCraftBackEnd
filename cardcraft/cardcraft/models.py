from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import default_storage

class CardSets(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=250)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=None)

class Card(models.Model):
    question = models.CharField(max_length=250)
    answer = models.CharField(max_length=250)
    set_id = models.ForeignKey(CardSets, on_delete=models.CASCADE, default=None)