from django.shortcuts import render
from rest_framework.views import APIView, Response
from rest_framework import status   
from home.models import *
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken

# Used to get tokens for user.
def get_tokens_for_user(user, role):
    refresh = RefreshToken.for_user(user)
    print(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'role': role
    }

# Used for login purpose.
class LoginView(APIView):
    def get(self, request):
        userName = request.data['userName']
        password = request.data['password']
        role = request.data['role']
        if role == "User":
            user = User.objects.filter(userName=userName).first()
            if user and check_password(password, user.password):
                areaRequest = Request.objects.filter(areaCode=user.areaCode)
                if areaRequest:
                    data= {"request": areaRequest}
                else:
                    data = {"data": "No Request"}
                response = {
                    "message": "Login Successful",
                    "success": True,
                    "data": data
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = {
                    "message": "Login Failed",
                    "success": False
                }
                return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        elif role == "Supervisor":        
            supervisor = Supervisor.objects.filter(userName=userName).first()
            if supervisor and check_password(password, supervisor.password):
                areaRequest = Request.objects.filter(areaCode=supervisor.areaCode)
                if areaRequest:
                    data= {"request": areaRequest}
                else:
                    data = {"data": "No Request"}
                response = {
                    "message": "Login Successful",
                    "success": True,
                    "data": data
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = {
                    "message": "Login Failed",
                    "success": False
                }
                return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        elif role == "Admin":
            admin = Admin.objects.fliter(userName=userName).first()
            if admin and check_password(password, admin.password):
                data = {} 
                response = {
                    "message": "Login Successful",
                    "success": True,
                    "data": data
                }   
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = {
                    "message": "Login Failed",
                    "success": False
                }

                return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        else:    
            response = {
                "message": "Invalid Role",
                "success": False
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

# Used to register user.        
class RegisterView(APIView):
    def post(self, request):
        # not checking for empty username and password to be checked on frontend side and also formate of suername(to improve sever efficiency)
        userName = request.data['userName']
        password = request.data['password']
        areaCode = request.data['areaCode']
        area = Area.objects.filter(areaCode=areaCode).first()
        obj = User.objects.create(userName=userName, password=password, areaCode=area)
        obj.save()
        response={
            "success": True,
            "message": "User added successfully"
        }
        return Response(response,status.HTTP_200_OK)

# Used to create request.
class CreateRequestView(APIView):
    def post(self, request):
        areaCode = request.data['areaCode']
        description = request.data['description']
        serviceCode = request.data['serviceCode']
        service = request.data['service']
        requestStatus = request.data['status']
        if not requestStatus or not service or not areaCode or not description or not serviceCode:
            response = {
                "success": False,
                "message": "Invalid Data"
            }
            return Response(response, status.HTTP_400_BAD_REQUEST)
        area = Area.objects.filter(areaCode=areaCode).first()
        obj = Request.objects.create(areaCode=area, description=description, serviceCode=serviceCode, service=service, status=requestStatus)
        obj.save()
        response = {
            "success": True,
            "message": "Request added successfully"
        }
        return Response(response, status.HTTP_200_OK)
        