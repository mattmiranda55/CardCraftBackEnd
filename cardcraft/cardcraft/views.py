from django.http import JsonResponse
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
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
from .serializers import UserSerializer
from .models import Card, CardSets




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
def makeCardSet(request):
    token = request.POST.get('jwt')
    notes = request.FILES.get('notes')
    cardsetName = request.POST.get('name')
    cardsetDescription = request.POST.get('description')

    # Veifies if user is logged in
    if not token:
        return JsonResponse({"message": "You are not logged in!"}) 
    
    try:
        payload = jwt.decode(token, 'CC', algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return JsonResponse({'message': 'Invalid web token'})

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            for chunk in notes.chunks():
                temp_file.write(chunk)
    
    file_path = temp_file.name

    qaPairs = utils.openAIRequest(file_path)

    os.unlink(file_path)

    # get user object
    user = User.objects.filter(id=payload['id']).first()

    # create Cardset object
    cardset = CardSets.objects.create(
        name = cardsetName,
        description = cardsetDescription,
        owner = user
    )

    # Save QA pairs in DB
    for key, value in qaPairs.items():
        Card.objects.create(
            question = value['question'],
            answer = value['answer'],
            set_id = cardset.id
        )

    return JsonResponse({'cardset': cardset.id})




@api_view(['POST'])
def deleteCardSet(request):
    pass





@api_view(['POST'])
def saveCardSet(request):
    data = json.loads(request.body)
    text = data.get('text')
    token = data.get('jwt')
    
    try:
        payload = jwt.decode(token, 'CC', algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return JsonResponse({'message': 'Invalid web token'})
    
    user = User.objects.filter(id=payload['id']).first()

    cardsetName = "name"

    pdf_path = utils.buildCardSetFile(text, user.username, cardsetName)

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
