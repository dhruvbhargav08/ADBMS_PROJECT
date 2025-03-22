import base64
import json
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.views import APIView, Response
from rest_framework import status   
from home.models import *
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken


def can_convert_to_int(s):
    """
    Checks if a given string can be converted to an integer.

    Args:
        s (str): Input string.

    Returns:
        bool: True if it can be converted, False otherwise.
    """
    try:
        int(s)  # Try converting to integer
        return True
    except ValueError:
        return False

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
            if not can_convert_to_int(requestId):
                return Response({"message": "Invalid Request Id", "success": False}, status=status.HTTP_400_BAD_REQUEST)
            requestId = int(requestId)
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
            return Response({"message": "Invalid Request Id", "success": False}, status=status.HTTP_400_BAD_REQUEST)

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

class GetManpower(APIView):
    """
    API endpoint to retrieve manpower data.

    Methods:
    --------
    get(request, workerType=None):
        - If workerType is provided, fetches the specific manpower record.
        - If workerType is not provided, fetches all manpower records.
        - Returns appropriate success or error messages.
    """

    def get(self, request, workerType=None):
        """
        Handles GET request to fetch manpower details.

        Parameters:
            request (HttpRequest): The HTTP request object.
            workerType (str, optional): The type of worker to fetch (e.g., 'Electrician', 'Mason').

        Returns:
            Response: JSON response containing manpower data or an error message.
        """
        if workerType:
            # Fetch manpower details for a specific worker type
            manpower_obj = ManPower.objects.filter(workerType=workerType).values().first()
            if manpower_obj:
                return Response(
                    {"success": True, "message": "Data fetched successfully", "data": {"manpower": manpower_obj}},
                    status=status.HTTP_200_OK
                )
            else:
                return Response({"success": False, "message": "No data found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Fetch all manpower records
            manpower = ManPower.objects.all()
            if not manpower.exists():
                return Response({"success": False, "message": "No data found"}, status=status.HTTP_404_NOT_FOUND)
            
            manpower_data = list(manpower.values())
            return Response(
                {"success": True, "message": "Data fetched successfully", "data": {"manpower": manpower_data}},
                status=status.HTTP_200_OK
            )

class GetMachine(APIView):
    """
    API endpoint to retrieve machine data.

    Methods:
    --------
    get(request, machineType=None):
        - If machineType is provided, fetches the specific machine record.
        - If machineType is not provided, fetches all machine records.
        - Returns appropriate success or error messages.
    """

    def get(self, request, machineType=None):
        """
        Handles GET request to fetch machine details.

        Parameters:
            request (HttpRequest): The HTTP request object.
            machineType (str, optional): The type of machine to fetch (e.g., 'Excavator', 'Bulldozer').

        Returns:
            Response: JSON response containing machine data or an error message.
        """
        if machineType:
            # Fetch machine details for a specific machine type
            machine_obj = Machine.objects.filter(machineType=machineType).values().first()
            if machine_obj:
                return Response(
                    {"success": True, "message": "Data fetched successfully", "data": {"machine": machine_obj}},
                    status=status.HTTP_200_OK
                )
            else:
                return Response({"success": False, "message": "No data found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Fetch all machine records
            machine = Machine.objects.all()
            if not machine.exists():
                return Response({"success": False, "message": "No data found"}, status=status.HTTP_404_NOT_FOUND)

            machine_data = list(machine.values())
            return Response(
                {"success": True, "message": "Data fetched successfully", "data": {"machines": machine_data}},
                status=status.HTTP_200_OK
            )

class GetMaterial(APIView):
    """
    API endpoint to retrieve material data.

    Methods:
    --------
    get(request, materialType=None):
        - If materialType is provided, fetches the specific material record.
        - If materialType is not provided, fetches all material records.
        - Returns appropriate success or error messages.
    """

    def get(self, request, materialType=None):
        """
        Handles GET request to fetch material details.

        Parameters:
            request (HttpRequest): The HTTP request object.
            materialType (str, optional): The type of material to fetch (e.g., 'Cement', 'Pipes').

        Returns:
            Response: JSON response containing material data or an error message.
        """
        if materialType:
            # Fetch material details for a specific material type
            material_obj = Material.objects.filter(materialType=materialType).values().first()
            if material_obj:
                return Response(
                    {"success": True, "message": "Data fetched successfully", "data": {"material": material_obj}},
                    status=status.HTTP_200_OK
                )
            else:
                return Response({"success": False, "message": "No data found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Fetch all material records
            material = Material.objects.all()
            if not material.exists():
                return Response({"success": False, "message": "No data found"}, status=status.HTTP_404_NOT_FOUND)

            material_data = list(material.values())
            return Response(
                {"success": True, "message": "Data fetched successfully", "data": {"materials": material_data}},
                status=status.HTTP_200_OK
            )
    
class GetRoad(APIView):
    """
    API endpoint to retrieve road data.

    Methods:
    --------
    get(request, roadId=None):
        - If roadId is provided, fetches the specific road record.
        - If roadId is not provided, fetches all road records.
        - Returns appropriate success or error messages.
    """

    def get(self, request, roadId=None):
        """
        Handles GET request to fetch road details.

        Parameters:
            request (HttpRequest): The HTTP request object.
            roadId (int, optional): The ID of the road to fetch.

        Returns:
            Response: JSON response containing road data or an error message.
        """
        if roadId:
            if not can_convert_to_int(roadId):
                return Response({"message": "Invalid Road Id", "success": False}, status=status.HTTP_400_BAD_REQUEST)
            roadId = int(roadId)
            # Fetch road details for a specific road ID
            road_obj = Road.objects.filter(roadId=roadId).values().first()
            if road_obj:
                return Response(
                    {"success": True, "message": "Data fetched successfully", "data": {"road": road_obj}},
                    status=status.HTTP_200_OK
                )
            else:
                return Response({"success": False, "message": "No data found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Fetch all road records
            roads = Road.objects.all()
            if not roads.exists():
                return Response({"success": False, "message": "No data found"}, status=status.HTTP_404_NOT_FOUND)

            road_data = list(roads.values())
            return Response(
                {"success": True, "message": "Data fetched successfully", "data": {"roads": road_data}},
                status=status.HTTP_200_OK
            )

class GetStreetLight(APIView):
    """
    API endpoint to retrieve street light data.

    Methods:
    --------
    get(request, streetLightId=None):
        - If streetLightId is provided, fetches the specific street light record.
        - If streetLightId is not provided, fetches all street light records.
        - Returns appropriate success or error messages.
    """

    def get(self, request, streetLightId=None):
        """
        Handles GET request to fetch street light details.

        Parameters:
            request (HttpRequest): The HTTP request object.
            streetLightId (int, optional): The ID of the street light to fetch.

        Returns:
            Response: JSON response containing street light data or an error message.
        """
        if streetLightId:
            if not can_convert_to_int(streetLightId):
                return Response({"message": "Invalid Street Light Id", "success": False}, status=status.HTTP_400_BAD_REQUEST)
            streetLightId = int(streetLightId)
            # Fetch street light details for a specific street light ID
            street_light_obj = StreetLight.objects.filter(streetLightId=streetLightId).values().first()
            if street_light_obj:
                return Response(
                    {"success": True, "message": "Data fetched successfully", "data": {"streetLight": street_light_obj}},
                    status=status.HTTP_200_OK
                )
            else:
                return Response({"success": False, "message": "No data found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Fetch all street light records
            street_lights = StreetLight.objects.all()
            if not street_lights.exists():
                return Response({"success": False, "message": "No data found"}, status=status.HTTP_404_NOT_FOUND)

            street_light_data = list(street_lights.values())
            return Response(
                {"success": True, "message": "Data fetched successfully", "data": {"streetLights": street_light_data}},
                status=status.HTTP_200_OK
            )
        
class GetDrainage(APIView):
    """
    API endpoint to retrieve drainage data.

    Methods:
    --------
    get(request, drainageId=None):
        - If drainageId is provided, fetches the specific drainage record.
        - If drainageId is not provided, fetches all drainage records.
        - Returns appropriate success or error messages.
    """

    def get(self, request, drainageId=None):
        """
        Handles GET request to fetch drainage details.

        Parameters:
            request (HttpRequest): The HTTP request object.
            drainageId (int, optional): The ID of the drainage to fetch.

        Returns:
            Response: JSON response containing drainage data or an error message.
        """
        if drainageId:
            if not can_convert_to_int(drainageId):
                return Response({"message": "Invalid Drainage Id", "success": False}, status=status.HTTP_400_BAD_REQUEST)
            drainageId = int(drainageId)
            # Fetch drainage details for a specific drainage ID
            drainage_obj = Drainage.objects.filter(drainageId=drainageId).values().first()
            if drainage_obj:
                return Response(
                    {"success": True, "message": "Data fetched successfully", "data": {"drainage": drainage_obj}},
                    status=status.HTTP_200_OK
                )
            else:
                return Response({"success": False, "message": "No data found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Fetch all drainage records
            drainages = Drainage.objects.all()
            if not drainages.exists():
                return Response({"success": False, "message": "No data found"}, status=status.HTTP_404_NOT_FOUND)

            drainage_data = list(drainages.values())
            return Response(
                {"success": True, "message": "Data fetched successfully", "data": {"drainages": drainage_data}},
                status=status.HTTP_200_OK
            )