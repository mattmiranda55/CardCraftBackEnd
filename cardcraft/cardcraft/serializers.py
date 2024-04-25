from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name']

class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ['id', 'question', 'answer', 'set_id']

class CardSetsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardSets
        fields = ['id', 'name', 'description', 'owner']