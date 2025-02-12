from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import UserCollection,RequisitionCollection
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
from bson import ObjectId
import requests

from dotenv import load_dotenv
import os
load_dotenv()

SECRET_KEY=os.getenv('SECRET_KEY')

import requests

def upload_to_file_io(file):
    url = "https://file.io"
    
    try:
        response = requests.post(url, files={"file": file})
        print("Status Code:", response.status_code)
        print("Raw Response:", response.text)  # Print raw response to debug

        if response.status_code == 200:
            response_json = response.json()
            print("Parsed JSON:", response_json)
            return response_json.get("link")

    except requests.exceptions.RequestException as e:
        print("Request Exception:", e)
    
    return None





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
        "password": request.data.get("password"),
        "role":request.data.get("role")
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
    
    access_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return JsonResponse({
        "access": access_token
    })


@api_view(['GET'])
def getUserByUsername(request, username):
    user = UserCollection.find_one({"username": username}, {"_id": 0, "password": 0})
    if not user:
        return JsonResponse({"error": "User not found"}, status=404)
    requisitions = list(RequisitionCollection.find({"username": username}))
    for req in requisitions:
        req["_id"] = str(req["_id"])
    user["requisitions"] = requisitions
    return JsonResponse(user, safe=False)




@api_view(['GET'])
def getAllUser(request):
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return JsonResponse({"error": "Authorization token required"}, status=401)

    token = auth_header.split(" ")[1] 

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user = UserCollection.find_one({"username": payload.get("username")})

        if not user:
            return JsonResponse({"error": "User not found"}, status=404)

        if user.get("role") != "servitor":
            return JsonResponse({"error": "Permission denied"}, status=403)

        users = list(UserCollection.find({}, {"_id": 0, "password": 0}))

        return JsonResponse({"users": users}, safe=False)

    except jwt.ExpiredSignatureError:
        return JsonResponse({"error": "Token has expired"}, status=401)
    except jwt.InvalidTokenError:
        return JsonResponse({"error": "Invalid token"}, status=401)

@api_view(['POST'])
def submitRequest(request):
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return JsonResponse({"error": "Authorization token required"}, status=401)

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return JsonResponse({"error": "Token has expired"}, status=401)
    except jwt.InvalidTokenError:
        return JsonResponse({"error": "Invalid token"}, status=401)

    user = UserCollection.find_one({"username": payload.get("username")})

    if not user:
        return JsonResponse({"error": "User not found"}, status=404)
    
    if user.get("role") != "customer":
            return JsonResponse({"error": "Permission denied"}, status=403)

    status = [
        {"stage": "submitted", "completed": True, "timestamp": datetime.datetime.utcnow()},
        {"stage": "viewed by staff", "completed": False, "timestamp": None},
        {"stage": "initiated", "completed": False, "timestamp": None},
        {"stage": "order dispatched", "completed": False, "timestamp": None},
        {"stage": "out for delivery", "completed": False, "timestamp": None},
        {"stage": "delivered", "completed": False, "timestamp": None}
    ]

    requisition = {
        "username": user["username"],
        "type": request.data.get("type", ""),
        "status": status,
        "servitor": "To be appointed",
        "detail": request.data.get("detail",""),
        "attachment": []

    }

    result = RequisitionCollection.insert_one(requisition)

    return JsonResponse({"message": "Requisition submitted successfully", "id": str(result.inserted_id)})

@api_view(['GET'])
def getRequi(request):
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return JsonResponse({"error": "Authorization token required"}, status=401)

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return JsonResponse({"error": "Token has expired"}, status=401)
    except jwt.InvalidTokenError:
        return JsonResponse({"error": "Invalid token"}, status=401)

    user = UserCollection.find_one({"username": payload.get("username")})

    if not user:
        return JsonResponse({"error": "User not found"}, status=404)
    
    if user.get("role") != "customer":
        return JsonResponse({"error": "Permission denied"}, status=403)
    
    fetchedReq = list(RequisitionCollection.find({"username": user.get("username")}, {"_id": 0}))

    return JsonResponse({"requisitions": fetchedReq}, safe=False)


@api_view(['GET'])
def getRequiForServitor(request):
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return JsonResponse({"error": "Authorization token required"}, status=401)

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return JsonResponse({"error": "Token has expired"}, status=401)
    except jwt.InvalidTokenError:
        return JsonResponse({"error": "Invalid token"}, status=401)

    user = UserCollection.find_one({"username": payload.get("username")})

    if not user:
        return JsonResponse({"error": "User not found"}, status=404)
    
    if user.get("role") != "servitor":
        return JsonResponse({"error": "Permission denied"}, status=403)
    
    fetchedReq = list(RequisitionCollection.find({}))

    for req in fetchedReq:
        req["_id"] = str(req["_id"])

    return JsonResponse({"requisitions": fetchedReq}, safe=False)

@api_view(['POST'])
def appointServitor(request, reqid):
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return JsonResponse({"error": "Authorization token required"}, status=401)

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return JsonResponse({"error": "Token has expired"}, status=401)
    except jwt.InvalidTokenError:
        return JsonResponse({"error": "Invalid token"}, status=401)

    user = UserCollection.find_one({"username": payload.get("username")})

    if not user:
        return JsonResponse({"error": "User not found"}, status=404)
    
    if user.get("role") != "servitor":
        return JsonResponse({"error": "Permission denied"}, status=403)
    
    try:
        obj_id = ObjectId(reqid)
    except:
        return JsonResponse({"error": "Invalid request ID format"}, status=400)

    requisition = RequisitionCollection.find_one({"_id": obj_id})

    if not requisition:
        return JsonResponse({"error": "Requisition not found"}, status=404)

    RequisitionCollection.update_one(
        {"_id": obj_id},
        {
            "$set": {
                "servitor": user["username"],
                "status.1.completed": True,
                "status.1.timestamp": datetime.datetime.utcnow()
            }
        }
    )

    return JsonResponse({"message": "Self-appointment successful"})

@api_view(['POST'])
def changeStatusForServitor(request, reqid, idx):
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return JsonResponse({"error": "Authorization token required"}, status=401)

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return JsonResponse({"error": "Token has expired"}, status=401)
    except jwt.InvalidTokenError:
        return JsonResponse({"error": "Invalid token"}, status=401)

    user = UserCollection.find_one({"username": payload.get("username")})

    if not user:
        return JsonResponse({"error": "User not found"}, status=404)
    
    if user.get("role") != "servitor":
        return JsonResponse({"error": "Permission denied"}, status=403)
    
    try:
        obj_id = ObjectId(reqid)
    except:
        return JsonResponse({"error": "Invalid request ID format"}, status=400)

    try:
        idx = int(idx)
    except ValueError:
        return JsonResponse({"error": "Invalid index format"}, status=400)

    requisition = RequisitionCollection.find_one({"_id": obj_id})

    if not requisition:
        return JsonResponse({"error": "Requisition not found"}, status=404)

    if idx < 0 or idx >= len(requisition.get("status", [])):
        return JsonResponse({"error": "Invalid status index"}, status=400)

    RequisitionCollection.update_one(
        {"_id": obj_id},
        {
            "$set": {
                f"status.{idx}.completed": True,
                f"status.{idx}.timestamp": datetime.datetime.utcnow()
            }
        }
    )

    return JsonResponse({"message": f"Status changed at index {idx}"})


@api_view(['POST'])
def uploadFile(request, reqid):
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return JsonResponse({"error": "Authorization token required"}, status=401)

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return JsonResponse({"error": "Token has expired"}, status=401)
    except jwt.InvalidTokenError:
        return JsonResponse({"error": "Invalid token"}, status=401)

    user = UserCollection.find_one({"username": payload.get("username")})

    if not user:
        return JsonResponse({"error": "User not found"}, status=404)
    
    try:
        obj_id = ObjectId(reqid)
    except:
        return JsonResponse({"error": "Invalid request ID format"}, status=400)

    requisition = RequisitionCollection.find_one({"_id": obj_id})

    if not requisition:
        return JsonResponse({"error": "Requisition not found"}, status=404)
    
    # print(request.FILES)
    
    if "File" not in request.FILES:
        return JsonResponse({"error": "No file uploaded"}, status=400)

    uploaded_file = request.FILES.get('File')
    if not uploaded_file:
        return JsonResponse({"error": "No file uploaded"}, status=400)
    
    try:
        link = upload_to_file_io(uploaded_file)
    except Exception as e:
        return JsonResponse({"error": f"File upload failed: {str(e)}"}, status=500)

    RequisitionCollection.update_one(
        {"_id": obj_id},
        {
            "$push": {"docs": link}
        }
    )

    return JsonResponse({"message": "File successfully attached", "file_link": link})





    
    

