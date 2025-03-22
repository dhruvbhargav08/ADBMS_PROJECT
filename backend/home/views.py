import base64
import json
from django.http import JsonResponse
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
    def post(self, request):
        userName = request.data['userName']
        password = request.data['password']
        role = request.data['role']
        if role == "User":
            user = User.objects.filter(userName=userName).first()
            if user and check_password(password, user.password):
                data = {"userName": user.userName, "areaCode": user.areaCode.areaCode}
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
                data = {"userName": supervisor.userName, "areaCode": supervisor.areaCode.areaCode}
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
            admin = Admin.objects.filter(userName=userName).first()
            if admin and check_password(password, admin.password):
                data = {"userName": admin.userName}
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
        if not area:
            response = {
                "success": False,
                "message": "Invalid Area Code"
            }
            return Response(response, status.HTTP_400_BAD_REQUEST)
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
        
# Used to get list of requests for a particular area.
class GetRequestsView(APIView):
    def get(self, request, requestId=None):
        if requestId:  
            request_obj = Request.objects.filter(requestId=requestId).values()[0]
            if request_obj:
                stats_obj = Stats.objects.filter(requestId=requestId).values().first()
                manpower_objs = ReqManpower.objects.filter(requestId=requestId).values()
                machine_objs = ReqMachine.objects.filter(requestId=requestId).values()
                material_objs = ReqMaterial.objects.filter(requestId=requestId).values()
                request = {      
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
                data = {"request": request}
                success = True 
                message = "Request fetched successfully" 
            else:
                data = {"request": "No Request"}
                success = False
                message = "Invalid Request Id"
        else:
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                return Response({"message": "Authorization header is required", "success": False}, status=status.HTTP_401_UNAUTHORIZED)
            try:
                _, encoded_data = auth_header.split(" ") 
                decoded_data = base64.b64decode(encoded_data).decode("utf-8")
                auth_data = json.loads(decoded_data)
            except Exception as e:
                return Response({"message": "Invalid Authorization header", "success": False}, status=status.HTTP_400_BAD_REQUEST)
            areaCode = auth_data.get("areaCode")
            if not areaCode:
                return Response({"message": "areaCode is required", "success": False}, status=status.HTTP_400_BAD_REQUEST)
            if "areaCode" not in request.data.keys():
                return Response({"message": "areaCode is required", "success": False}, status=status.HTTP_400_BAD_REQUEST)
            areaCode = request.data['areaCode'] 
            if not areaCode:
                return Response({"message": "areaCode is required", "success": False}, status=status.HTTP_400_BAD_REQUEST)
            area = Area.objects.filter(areaCode=areaCode).first()
            if not area:
                return Response({"message": "Invalid areaCode", "success": False}, status=status.HTTP_404_NOT_FOUND)
            areaRequests = Request.objects.filter(areaCode=area).values()
            requests = []
            for areaRequest in areaRequests:
                request = {      
                            "requestId": areaRequest['requestId'],
                            "areaCode_id": areaRequest['areaCode_id'],
                            "service": areaRequest['service'],
                            "serviceCode": areaRequest['serviceCode'],
                            "description": areaRequest['description'],
                            "progress": areaRequest['progress'],
                            "status": areaRequest['status']
                        }
                requests.append(request)
            data = {"requests": requests if requests else "No Request"}
            message = "Requests fetched successfully" if requests else "No Requests"
            success = True if requests else False
        response = {
            "message": message,
            "success": success,
            "data": data
        }
        return Response(response, status=status.HTTP_200_OK)