from django.http import JsonResponse
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
import jwt
import datetime
import json
import tempfile
import os
from cardcraft import utils
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from .serializers import UserSerializer, CardSetsSerializer
from .models import CardSets, Card

@api_view(['POST'])
@csrf_exempt
def loginUser(request):   
    data = json.loads(request.body)
    email = data.get('email')
    password = data.get('password')
    
    user = User.objects.filter(email=email).first()
    
    if user is None:
        return JsonResponse({'message': 'Invalid email'})
    if not user.check_password(password):
        return JsonResponse({'message': 'Incorrect Password'})
    
    payload = {
        'id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=120),
        'iat': datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, 'CC', algorithm='HS256') 

    print("Login Successful")
    return JsonResponse({'jwt': token})  

# Return info from authenticated user
@api_view(['POST'])
def userInfo(request):

    if request.method == 'POST':
        data = json.loads(request.body)
        token = data.get('jwt')

        if not token:
            return JsonResponse({'message': 'You are not signed in'})

        try:
            payload = jwt.decode(token, 'CC', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'message': 'Invalid web token'})

        user = User.objects.filter(id=payload['id']).first()
        user_serializer = UserSerializer(user)

        return Response(user_serializer.data)

@api_view(['POST'])
def createUser(request):
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    hashed_password = make_password(password)

    if is_email_taken(email):
        return JsonResponse({'message': "Email is already taken"})  
    if is_username_taken(username):
        return JsonResponse({'message': "Username is already taken"})
        
    new_user = User.objects.create(
        username=username, 
        email=email, 
        password=hashed_password, 
        first_name=first_name, 
        last_name=last_name
    )
    
    return JsonResponse({
                        'id': new_user.id, 
                         'message': 'User Created Succesfully'
                        })

@api_view(['POST'])
def changePassword(request):
    data = json.loads(request.body)
    token = data.get('jwt')
    password = data.get('password')
    new_password = data.get('new_password')

    if not token:
        return JsonResponse({"message": "You are not logged in!"})

    # validating jwt token
    try:
        payload = jwt.decode(token, 'CC', algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return JsonResponse({'message': 'Invalid web token'})  
    
    # find user by id, using jwt
    user = User.objects.filter(id=payload['id']).first()

    # if user not found
    if user is None:
        return JsonResponse({'message': 'User not found'})
    
    # Check if the current password is correct
    # Change password if correct
    if authenticate(username=user.username, password=password):
        user.set_password(new_password)
        user.save()
        return JsonResponse({'message': 'Password changed successfully'}, status=200)
    else:
        return JsonResponse({'message': 'Current password is incorrect'}, status=400)

@api_view(['POST'])
@csrf_exempt
@parser_classes((JSONParser, MultiPartParser))
def makeCardSet(request):
    token = request.data.get('jwt')
    notes = request.FILES.get('notes')
    name = request.data.get('name')
    description = request.data.get('description')

    # validating jwt token
    if not token:
        return JsonResponse({"message": "You are not logged in!"})
    try:
        payload = jwt.decode(token, 'CC', algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return JsonResponse({'message': 'Invalid web token'})

    user = User.objects.filter(id=payload['id']).first()
    if user is None:
        return JsonResponse({'message': 'User not found'})

    if notes is None:
        return JsonResponse({"message": "File is not provided!"})

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        for chunk in notes.chunks():
            temp_file.write(chunk)

    file_path = temp_file.name
    openAIResponse = utils.openAIRequest(file_path)
    os.unlink(file_path)

    # Ensure openAIResponse is a dictionary
    if isinstance(openAIResponse, str):
        openAIResponse = json.loads(openAIResponse)

    # Create a new CardSet
    cardset = CardSets.objects.create(
        name=name,
        description=description,
        owner=user
    )

    # Dynamically create cards based on the openAIResponse content
    i = 1
    while f"question-{i}" in openAIResponse:
        question_key = f"question-{i}"
        answer_key = f"answer-{i}"
        Card.objects.create(
            question=openAIResponse[question_key],
            answer=openAIResponse[answer_key],
            set_id=cardset
        )
        i += 1

    return JsonResponse({'cardset': cardset.id})

@api_view(['DELETE'])
def deleteCardSet(request):
    cardsetID = request.data.get('id')

    cardset = CardSets.objects.filter(id = cardsetID)

    cardset.delete()

    return JsonResponse({'message': 'CardSet Deleted Successfully'})

@api_view(['POST'])
def getCardSet(request):
    cardsetID = request.data.get('id')

    cards = Card.objects.filter(set_id=cardsetID)

    cardsetInfo = CardSets.objects.filter(id = cardsetID)

    cardset = {}
    for index, card in enumerate(cards, start=1):
        cardset[f'question-{index}'] = card.question
        cardset[f'answer-{index}'] = card.answer

    return JsonResponse({'cardset': cardset, 'name': cardsetInfo.name, 'description': cardsetInfo.description})

@api_view(['POST'])
def getCardSetsByUser(request):
    data = json.loads(request.body)
    token = data.get('jwt')

    if not token:
        return JsonResponse({"message": "You are not logged in!"})
    try:
        payload = jwt.decode(token, 'CC', algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return JsonResponse({'message': 'Invalid web token'})
    
    user = User.objects.filter(id=payload['id']).first()

    cardsets = CardSets.objects.filter(owner = user)

    cardsets = CardSetsSerializer(cardsets, many=True)

    return Response({'cardsets': cardsets.data})

@api_view(['POST'])
def saveCardSet(request):
    data = json.loads(request.body)
    token = data.get('jwt')
    cardsetID = data.get('id')
    
    try:
        payload = jwt.decode(token, 'CC', algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return JsonResponse({'message': 'Invalid web token'})
    
    cards = Card.objects.filter(set_id=cardsetID)
    cardsetJSON = {}
    for index, card in enumerate(cards, start=1):
        cardsetJSON[f'question-{index}'] = card.question
        cardsetJSON[f'answer-{index}'] = card.answer
    
    user = User.objects.filter(id=payload['id']).first()

    cardset = CardSets.objects.filter(id=cardsetID).first()

    pdf_path = utils.buildCardSetFile(cardsetJSON, user.username, cardset.name)

    return JsonResponse({'pdf': pdf_path})

########################################################
#
# Helper methods
#
########################################################
def is_email_taken(email):
    try:
        user = User.objects.get(email=email)
        return True
    except User.DoesNotExist:
        return False
    
def is_username_taken(username):
    try:
        user = User.objects.get(username=username)
        return True
    except User.DoesNotExist:
        return False
