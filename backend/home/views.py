from django.shortcuts import render
from rest_framework.views import APIView, Response
from rest_framework import status   
from home.models import User, Supervisor, Admin
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken

# Create your views here.

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class LoginView(APIView):
    def get(self, request):
        userName = request.GET.get('userName')
        password = request.GET.get('password')
        role = request.GET.get('role')
        if role == "User":
            user = User.objects.get(userName=userName)
            if user and check_password(password, user.password):
                # add code for the data to be display content 
                tokens = get_tokens_for_user(user)
                data= {"tokens": tokens}
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
            supervisor = Supervisor.objects.get(userName=userName)
            if supervisor and check_password(password, supervisor.password):
                # add code for the data to be display content 
                tokens = get_tokens_for_user(supervisor)
                data = {"tokens": tokens} 
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
            admin = Admin.objects.get(userName=userName)
            if admin and check_password(password, admin.password):
                # add code for the data to be display content 
                tokens = get_tokens_for_user(admin)
                data = {"tokens": tokens} 
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
        
class RegisterView(APIView):
    def post(self, request):
        # not checking for empty username and password to be checked on frontend side and also formate of suername(to improve sever efficiency)
        userName = request.data['userName']
        password = request.data['password']
        obj = User.objects.create(userName=userName, password=password)
        obj.save()
        response={
            "success": True,
            "message": "User added successfully"
        }
        return Response(response,status.HTTP_200_OK)