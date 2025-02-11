from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import UserCollection
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse

from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
import datetime
import jwt

from dotenv import load_dotenv
import os
load_dotenv()

@api_view(['GET'])
def getData(request):
    person={'name':'Dennis','age':35}
    return Response(person)

def index(request):
    return HttpResponse("<h1>App is running..</h1>")

@api_view(['GET'])
def add_person(request):
    records={
        "first_name":"hohn"
    }
    result = UserCollection.insert_one(records)
    return HttpResponse("New Person is added")

@api_view(['GET'])
def get_all_person(request):
    persons = list(UserCollection.find({}, {"_id": 0})) 
    return Response({"data": persons}) 




@api_view(['POST'])
def register(request):
    records = {
        "username": request.data.get("username"),
        "password": request.data.get("password")
    }

    if not records["username"] or not records["password"]:
        return JsonResponse({"error": "All fields are required"}, status=400)

    if UserCollection.find_one({"username": records["username"]}):
        return JsonResponse({"error": "Username already taken"}, status=400)

    records["password"] = make_password(records["password"])
    UserCollection.insert_one(records)

    return JsonResponse({"message": "User registered successfully"})


@api_view(['POST'])
def login(request):
    records = {
        "username": request.data.get("username"),
        "password": request.data.get("password")
    }

    user = UserCollection.find_one({"username": records["username"]})
    
    if not user or not make_password(user["password"], records["password"]):
        return JsonResponse({"error": "Invalid credentials"}, status=401)

    payload = {
        "id": str(user["_id"]),
        "username": user["username"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
        "iat": datetime.datetime.utcnow()
    }
    
    access_token = jwt.encode(payload, os.getenv('SECRET_KEY'), algorithm="HS256")

    return JsonResponse({
        "access": access_token
    })