from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import default_storage

class CardSets(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    file = models.FileField(upload_to="cardsets/", null=True, blank=True)

class Card(models.Model):
    question = models.CharField()
    answer = models.CharField()
    set_id = models.ForeignKey(CardSets, on_delete=models.CASCADE, default=None)