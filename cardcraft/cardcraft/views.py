from django.http import JsonResponse
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
import jwt
import datetime
import json
import utils
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate

@api_view(['POST'])
@csrf_exempt
def loginUser(request):   
    # Get the request data as a dictionary
    data = json.loads(request.body)
    email = data.get('email')
    password = data.get('password')
    
    # find user by email in request payload
    user = User.objects.filter(email=email).first()
    
    # if user not found
    if user is None:
        return JsonResponse({'message': 'Invalid email'})
    
    # checking password match, check_passwords checks hashed passwords
    if not user.check_password(password):
        return JsonResponse({'message': 'Incorrect Password'})
    
    # creating jwt token
    payload = {
        'id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=120),
        'iat': datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, 'CC', algorithm='HS256')  # second param is secret key for hashing

    # if succesful login 
    print("Login Successful")
    
    # returning jwt token
    # frontend will store token into localstorage
    return JsonResponse({'jwt': token})    

@api_view(['GET'])
def makeCardSet(request):
    pass

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
    
    return JsonResponse({'id': new_user.id})
    

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
def deleteCardSet(request):
    pass

@api_view(['POST'])
def updateCardSet(request):
    pass

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
