import base64
import json
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.views import APIView, Response
from rest_framework import status   
from home.models import *
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user, role):
    """
    Generate JWT tokens (access and refresh) for a given user.
    
    Args:
        user: The user instance.
        role: The role of the user (User, Supervisor, Admin).
    
    Returns:
        A dictionary containing the refresh and access tokens, along with the user role.
    """
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'role': role
    }

class LoginView(APIView):
    """
    API endpoint for user login based on role (User, Supervisor, Admin).
    """
    def post(self, request):
        """
        Handle login requests by verifying credentials and returning a response.
        """
        userName = request.data['userName']
        password = request.data['password']
        role = request.data['role']

        # Check for User role
        if role == "User":
            user = User.objects.filter(userName=userName).first()
            if user and check_password(password, user.password):
                data = {"userName": user.userName, "areaCode": user.areaCode.areaCode}
                response = {"message": "Login Successful", "success": True, "data": data}
                return Response(response, status=status.HTTP_200_OK)
            
        # Check for Supervisor role
        elif role == "Supervisor":        
            supervisor = Supervisor.objects.filter(userName=userName).first()
            if supervisor and check_password(password, supervisor.password):
                data = {"userName": supervisor.userName, "areaCode": supervisor.areaCode.areaCode}
                response = {"message": "Login Successful", "success": True, "data": data}
                return Response(response, status=status.HTTP_200_OK)
        
        # Check for Admin role
        elif role == "Admin":
            admin = Admin.objects.filter(userName=userName).first()
            if admin and check_password(password, admin.password):
                data = {"userName": admin.userName}
                response = {"message": "Login Successful", "success": True, "data": data}
                return Response(response, status=status.HTTP_200_OK)
        
        # Invalid role or credentials
        response = {"message": "Login Failed", "success": False}
        return Response(response, status=status.HTTP_401_UNAUTHORIZED)

class RegisterView(APIView):
    """
    API endpoint for user registration.
    """
    def post(self, request):
        """
        Register a new user with the given details.
        """
        userName = request.data['userName']
        password = request.data['password']
        areaCode = request.data['areaCode']
        
        # Validate area code
        area = Area.objects.filter(areaCode=areaCode).first()
        if not area:
            return Response({"success": False, "message": "Invalid Area Code"}, status.HTTP_400_BAD_REQUEST)
        
        # Create new user
        obj = User.objects.create(userName=userName, password=password, areaCode=area)
        obj.save()
        response = {"success": True, "message": "User added successfully"}
        return Response(response, status.HTTP_200_OK)

class RequestView(APIView):
    """
    API endpoint to handle requests related to services.
    """
    def post(self, request):
        """
        Create a new service request.
        """
        areaCode = request.data['areaCode']
        description = request.data['description']
        serviceCode = request.data['serviceCode']
        service = request.data['service']
        requestStatus = request.data['status']

        # Validate input data
        if not requestStatus or not service or not areaCode or not description or not serviceCode:
            return Response({"success": False, "message": "Invalid Data"}, status.HTTP_400_BAD_REQUEST)

        area = Area.objects.filter(areaCode=areaCode).first()
        obj = Request.objects.create(areaCode=area, description=description, serviceCode=serviceCode, service=service, status=requestStatus)
        obj.save()
        return Response({"success": True, "message": "Request added successfully"}, status.HTTP_200_OK)
    
    def get(self, request, requestId=None):
        """
        Fetch service requests based on request ID or area code.
        """
        if requestId:  
            request_obj = Request.objects.filter(requestId=requestId).values().first()
            if request_obj:
                stats_obj = Stats.objects.filter(requestId=requestId).values().first()
                manpower_objs = ReqManpower.objects.filter(requestId=requestId).values()
                machine_objs = ReqMachine.objects.filter(requestId=requestId).values()
                material_objs = ReqMaterial.objects.filter(requestId=requestId).values()
                request_data = {      
                    "requestId": request_obj['requestId'],
                    "areaCode_id": request_obj['areaCode_id'],
                    "service": request_obj['service'],
                    "serviceCode": request_obj['serviceCode'],
                    "description": request_obj['description'],
                    "progress": request_obj['progress'],
                    "status": request_obj['status'],
                    "raiseDate": stats_obj["raiseDate"] if stats_obj else "",
                    "startDate": stats_obj["startDate"] if stats_obj else "",
                    "finishDate": stats_obj["finishDate"] if stats_obj else "",
                    "manpower": list(manpower_objs),
                    "machines": list(machine_objs),
                    "materials": list(material_objs)
                }
                return Response({"message": "Request fetched successfully", "success": True, "data": request_data}, status=status.HTTP_200_OK)
            return Response({"message": "Invalid Request Id", "success": False, "data": "No Request"}, status=status.HTTP_400_BAD_REQUEST)

        # Authorization header processing
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return Response({"message": "Authorization header is required", "success": False}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            _, encoded_data = auth_header.split(" ") 
            decoded_data = base64.b64decode(encoded_data).decode("utf-8")
            auth_data = json.loads(decoded_data)
        except Exception:
            return Response({"message": "Invalid Authorization header", "success": False}, status=status.HTTP_400_BAD_REQUEST)
        
        areaCode = auth_data.get("areaCode")
        area = Area.objects.filter(areaCode=areaCode).first()
        if not area:
            return Response({"message": "Invalid areaCode", "success": False}, status=status.HTTP_404_NOT_FOUND)
        
        areaRequests = Request.objects.filter(areaCode=area).values()
        return Response({"message": "Requests fetched successfully", "success": True, "data": list(areaRequests)}, status=status.HTTP_200_OK)