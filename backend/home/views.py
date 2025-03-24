import base64
import json
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.views import APIView, Response
from rest_framework import status   
from home.models import *
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.timezone import now
from home.area import *
from home.drainage import *
from home.streetLight import *


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
            if user:
                if check_password(password, user.password):
                    data = {
                            "userName": user.userName, 
                            "areaCode": user.areaCode.areaCode
                        }
                    return Response(
                                {
                                    "message": "Login Successful", 
                                    "success": True, 
                                    "data": data
                                }, 
                                status=status.HTTP_200_OK
                            )
                else:
                    return Response(
                                {
                                    "message": "Login failed. \nUsername password do not match", 
                                    "success": False
                                }, 
                                status=status.HTTP_401_UNAUTHORIZED
                            )
            else:
                return Response(    
                            {   
                                "message": "User not found", 
                                "success": False
                            }, 
                            status=status.HTTP_401_UNAUTHORIZED
                        )
        # Check for Supervisor role
        elif role == "Supervisor":        
            supervisor = Supervisor.objects.filter(userName=userName).first()
            if supervisor:
                if check_password(password, supervisor.password):
                    data = {
                            "userName": supervisor.userName, 
                            "areaCode": supervisor.areaCode.areaCode
                        }
                    return Response(
                                {
                                    "message": "Login Successful", 
                                    "success": True, 
                                    "data": data
                                }, 
                                status=status.HTTP_200_OK
                            )
                else:
                    return Response(
                                {
                                    "message": "Login failed \nUsername password do not match", 
                                    "success": False
                                }, 
                                status=status.HTTP_401_UNAUTHORIZED
                            )
            else:
                return Response(
                            {
                                "message": "Supervisor not found", 
                                "success": False
                            }, 
                            status=status.HTTP_401_UNAUTHORIZED
                        )
        # Check for Admin role
        elif role == "Admin":
            admin = Admin.objects.filter(userName=userName).first()
            if admin: 
                if check_password(password, admin.password):
                    data = {
                            "userName": admin.userName
                        }
                    return Response(
                                {
                                    "message": "Login Successful", 
                                    "success": True, 
                                    "data": data
                                }, 
                                status=status.HTTP_200_OK
                            )
                else:
                    return Response(
                                {
                                    "message": "Login failed \nUsername password do not match", 
                                    "success": False
                                }, 
                                status=status.HTTP_401_UNAUTHORIZED
                            )
            else:
                return Response(
                            {
                                "message": "Admin not found", 
                                "success": False
                            }, 
                            status=status.HTTP_401_UNAUTHORIZED
                        )
        # Invalid role or credentials
        return Response(
                    {
                        "message": "Login Failed", 
                        "success": False
                    }, 
                    status=status.HTTP_401_UNAUTHORIZED
                )

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
        if not password or not userName or not areaCode:
            # this checking will be done on frontend. check whether username, password or areaCode is filled or not.
            pass
        # Check if username already exists
        if User.objects.filter(userName=userName).exists():
            return Response(
                        {
                            "success": False, 
                            "message": "Username already taken"
                        }, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

        # Validate area code
        area = Area.objects.filter(areaCode=areaCode).first()
        if not area:
            return Response(
                        {
                            "success": False, 
                            "message": "Invalid Area Code"
                        }, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
        # Create new user
        obj = User.objects.create(userName=userName, password=password, areaCode=area)
        obj.save()
        return Response(
                    {
                        "success": True, 
                        "message": "User added successfully"
                    }, 
                    status=status.HTTP_200_OK
                )

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
            return Response(
                        {
                            "success": False, 
                            "message": "Invalid Data"
                        }, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
        area = Area.objects.filter(areaCode=areaCode).first()
        if not area:
            return Response(
                        {
                            "success": False, 
                            "message": "Invalid Area Code"
                        }, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
        obj = Request.objects.create(areaCode=area, description=description, serviceCode=serviceCode, service=service, status=requestStatus)
        Stats.objects.create(requestId=obj, raiseDate=now())
        return Response(
                    {
                        "success": True, 
                        "message": "Request added successfully"
                    }, 
                    status=status.HTTP_200_OK
                )
    
    def get(self, request, requestId=None):
        """
        Fetch service requests based on request ID or area code.
        """
        if requestId:  
            if not can_convert_to_int(requestId):
                return Response(
                            {
                                "message": "Invalid Request Id", 
                                "success": False,
                                "data": []
                            }, 
                            status=status.HTTP_400_BAD_REQUEST
                        )
            requestId = int(requestId)
            request_obj = Request.objects.filter(requestId=requestId).values().first()
            if request_obj:
                stats_obj = Stats.objects.filter(requestId=requestId).values().first()
                manpower_objs = list(ReqManpower.objects.filter(requestId=requestId).values())
                manpowerData = list()
                for manpower_obj in manpower_objs:
                    manpowerData.append(
                                {
                                    "id": manpower_obj["workerType_id"],
                                    "workerType": manpower_obj["workerType_id"],
                                    "workerCount": manpower_obj["workerCount"]
                                }
                            )
                machine_objs = ReqMachine.objects.filter(requestId=requestId).values()
                machineData = list()
                for machine_obj in machine_objs:
                    machineData.append(
                                {
                                    "id": machine_obj["machineType_id"],
                                    "machineType": machine_obj["machineType_id"],
                                    "machineCount": machine_obj["machineCount"]
                                }
                            )
                material_objs = ReqMaterial.objects.filter(requestId=requestId).values()
                materialData = list()
                for material_obj in material_objs:
                    materialData.append(
                                {
                                    "id": material_obj["materialType_id"],
                                    "materialType": material_obj["materialType_id"],
                                    "materialCount": material_obj["materialCount"]
                                }
                            )
                request_data = {
                                "id": request_obj['requestId'],
                                "requestId": request_obj['requestId'],
                                "areaCode": request_obj['areaCode_id'],
                                "service": request_obj['service'],
                                "serviceCode": request_obj['serviceCode'],
                                "description": request_obj['description'],
                                "progress": request_obj['progress'],
                                "status": request_obj['status'],
                                "raiseDate": stats_obj["raiseDate"] if stats_obj else "",
                                "startDate": stats_obj["startDate"] if stats_obj else "",
                                "finishDate": stats_obj["finishDate"] if stats_obj else "",
                                "manpower": manpowerData,
                                "machines": machineData,
                                "materials": materialData
                            }
                return Response(
                            {
                                "message": "Request fetched successfully", 
                                "success": True, 
                                "data": request_data
                            }, 
                            status=status.HTTP_200_OK
                        )
            return Response(
                        {
                            "message": "No request found with this request Id",
                            "success": False, 
                            "data": []
                        }, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

        # Authorization header processing
        # auth_header = request.headers.get("Authorization")
        # if not auth_header:
        #     return Response({"message": "Authorization header is required", "success": False}, status=status.HTTP_401_UNAUTHORIZED)
        # try:
        #     _, encoded_data = auth_header.split(" ") 
        #     decoded_data = base64.b64decode(encoded_data).decode("utf-8")
        #     auth_data = json.loads(decoded_data)
        # except Exception:
        #     return Response({"message": "Invalid Authorization header", "success": False}, status=status.HTTP_400_BAD_REQUEST)
        
        # areaCode = auth_data.get("areaCode")
        elif "areaCode" in request.data.keys():
            areaCode = request.data['areaCode']
            area = Area.objects.filter(areaCode=areaCode).first()
            if not area:
                return Response(
                            {
                                "message": "Invalid areaCode", 
                                "success": False, 
                                "data": []
                            }, 
                            status=status.HTTP_404_NOT_FOUND
                        )
            areaRequests = Request.objects.filter(areaCode=area).values()
            requests = []
            for areaRequest in areaRequests:
                requests.append(
                            {
                                "id": areaRequest['requestId'],
                                "requestId": areaRequest['requestId'],
                                "areaCode": areaRequest['areaCode_id'],
                                "service": areaRequest['service'],
                                "serviceCode": areaRequest['serviceCode'],
                                "description": areaRequest['description'],
                                "progress": areaRequest['progress'],
                                "status": areaRequest['status']
                            }
                        )
            if requests:
                return Response(
                            {
                                "message": "Requests fetched successfully", 
                                "success": True, 
                                "data": requests
                            }, 
                            status=status.HTTP_200_OK
                        )
            else:
                return Response(
                            {
                                "message": "No request found", 
                                "success": True, 
                                "data": []
                            }, 
                            status=status.HTTP_200_OK
                        )
        else:
            AllRequests = Request.objects.all().values()
            requests = []
            for AllRequest in AllRequests:
                requests.append(
                            {
                                "id": AllRequest['requestId'],
                                "requestId": AllRequest['requestId'],
                                "areaCode": AllRequest['areaCode_id'],
                                "service": AllRequest['service'],
                                "serviceCode": AllRequest['serviceCode'],
                                "description": AllRequest['description'],
                                "progress": AllRequest['progress'],
                                "status": AllRequest['status']
                            }
                        )
            return Response(
                        {
                            "message": "Requests fetched successfully", 
                            "success": True, 
                            "data": requests
                        }, 
                        status=status.HTTP_200_OK
                    )    
    
    def put(self, request, requestId):
        """
        Update an existing service request.
        """
        try:
            data = request.data

            # Fetch existing request
            try:
                req = Request.objects.get(pk=requestId)
            except Request.DoesNotExist:
                return Response({"message": "Request not found", "success": False, "data": []}, status=status.HTTP_404_NOT_FOUND)

            # Validate and update basic request fields
            req.areaCode_id = data.get("areaCode", req.areaCode_id)
            req.service = data.get("service", req.service)
            req.serviceCode = data.get("serviceCode", req.serviceCode)
            req.description = data.get("description", req.description)
            req.progress = data.get("progress", req.progress)
            req.status = data.get("status", req.status)
            # need to work with the priority field
            req.save()

            # Update Stats (startDate and finishDate based on status)
            stats, _ = Stats.objects.get_or_create(requestId=req)

            if req.status == "Under work" and not stats.startDate:
                stats.startDate = now()  # Set start date when work begins

            if req.status == "Completed" and not stats.finishDate:
                stats.finishDate = now()  # Set finish date when work is completed

            stats.save()

            # Update Manpower
            for mp in data.get("manpower", []):
                worker_type = mp.get("workerType")
                worker_count = mp.get("workerCount")

                if not worker_type or worker_count is None:
                    continue

                # Check if the worker type exists
                manpower_obj = ManPower.objects.filter(workerType=worker_type).first()
                if not manpower_obj:
                    return Response({
                        "message": f"Worker type '{worker_type}' not found.",
                        "success": False
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Fetch existing assigned manpower request
                req_manpower, created = ReqManpower.objects.get_or_create(
                    requestId=req, workerType=manpower_obj,
                    defaults={"workerCount": 0}
                )

                # Release previously assigned manpower before checking availability
                manpower_obj.workerCount += req_manpower.workerCount

                # Check if enough manpower is available
                if manpower_obj.workerCount < worker_count:
                    return Response({
                        "message": f"Not enough {worker_type}s available. Requested: {worker_count}, Available: {manpower_obj.workerCount}",
                        "success": False
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Assign new count and update manpower
                req_manpower.workerCount = worker_count
                req_manpower.save()

                manpower_obj.workerCount -= worker_count
                manpower_obj.save()

            # Update Machines
            for mach in data.get("machines", []):
                machine_type = mach.get("machineType")
                machine_count = mach.get("machineCount")

                if not machine_type or machine_count is None:
                    continue

                # Check if the machine type exists
                machine_obj = Machine.objects.filter(machineType=machine_type).first()
                if not machine_obj:
                    return Response({
                        "message": f"Machine type '{machine_type}' not found.",
                        "success": False
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Fetch existing assigned machine request
                req_machine, created = ReqMachine.objects.get_or_create(
                    requestId=req, machineType=machine_obj,
                    defaults={"machineCount": 0}
                )

                # Release previously assigned machines
                machine_obj.machineCount += req_machine.machineCount

                # Check if enough machines are available
                if machine_obj.machineCount < machine_count:
                    return Response({
                        "message": f"Not enough {machine_type}s available. Requested: {machine_count}, Available: {machine_obj.machineCount}",
                        "success": False
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Assign new count and update available machines
                req_machine.machineCount = machine_count
                req_machine.save()

                machine_obj.machineCount -= machine_count
                machine_obj.save()
                

            # Update Materials
            for mat in data.get("materials", []):
                material_type = mat.get("materialType")
                material_count = mat.get("materialCount")

                if not material_type or material_count is None:
                    continue

                # Check if the material type exists
                material_obj = Material.objects.filter(materialType=material_type).first()
                if not material_obj:
                    return Response({
                        "message": f"Material type '{material_type}' not found.",
                        "success": False
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Fetch existing assigned material request
                req_material, created = ReqMaterial.objects.get_or_create(
                    requestId=req, materialType=material_obj,
                    defaults={"materialCount": 0}
                )

                # Release previously assigned materials
                material_obj.materialCount += req_material.materialCount

                # Check if enough materials are available
                if material_obj.materialCount < material_count:
                    return Response({
                        "message": f"Not enough {material_type} available. Requested: {material_count}, Available: {material_obj.materialCount}",
                        "success": False
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Assign new count and update available materials
                req_material.materialCount = material_count
                req_material.save()

                material_obj.materialCount -= material_count
                material_obj.save()

            return Response({"message": "Request updated successfully", "success": True}, status=status.HTTP_200_OK)

        except json.JSONDecodeError:
            return Response({"message": "Invalid JSON", "success": False}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"message": str(e), "success": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ManpowerView(APIView):
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
                manpower_data = {
                                "id": manpower_obj["workerType"],
                                "workerType": manpower_obj["workerType"],
                                "workerCount": manpower_obj["workerCount"]
                            }
                return Response(
                        {
                            "success": True, 
                            "message": "Data fetched successfully", 
                            "data": manpower_data
                        },
                        status=status.HTTP_200_OK
                    )
            else:
                return Response(
                        {
                            "success": False, 
                            "message": "No data found",
                            "data": []
                        }, 
                        status=status.HTTP_404_NOT_FOUND
                    )
        else:
            # Fetch all manpower records
            manpower = ManPower.objects.all()
            if not manpower.exists():
                return Response(
                        {
                            "success": False, 
                            "message": "No data found", 
                            "data": []
                        }, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            manpower_data = list(manpower.values())
            manpowerData = []
            for manpower in manpower_data:
                manpowerData.append(
                                {
                                    "id": manpower["workerType"],
                                    "workerType": manpower["workerType"],
                                    "workerCount": manpower["workerCount"]
                                }
                            )
            return Response(
                        {
                            "success": True, 
                            "message": "Data fetched successfully", 
                            "data": manpowerData
                        },
                        status=status.HTTP_200_OK
                    )
    
    def post(self, request):
        worker_type = request.data["workerType"]
        worker_count = request.data["workerCount"]

        if not worker_type or worker_count is None:
            return Response(
                {"success": False, "message": "workerType and workerCount are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if worker_type not in dict(ManPower.WORKER_TYPES):
            return Response(
                {"success": False, "message": "Invalid workerType."},
                status=status.HTTP_400_BAD_REQUEST
            )

        manpower, created = ManPower.objects.update_or_create(
            workerType=worker_type, defaults={"workerCount": worker_count}
        )

        if created:
            return Response(
                {"success": True, "message": "Worker added successfully."},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"success": True, "message": "Worker count updated successfully."},
                status=status.HTTP_200_OK
            )
        

class MachineView(APIView):
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
                machine_data = {
                                "id": machine_obj["machineType"],
                                "machineType": machine_obj["machineType"],
                                "machineCount": machine_obj["machineCount"]
                                }
                return Response(
                            {
                                "success": True, 
                                "message": "Data fetched successfully", 
                                "data":machine_data
                            },
                            status=status.HTTP_200_OK
                        )
            else:
                return Response(
                            {
                                "success": False, 
                                "message": "No data found", 
                                "data": []
                            }, 
                            status=status.HTTP_404_NOT_FOUND
                        )
        else:
            # Fetch all machine records
            machine = Machine.objects.all()
            if not machine.exists():
                return Response(
                            {
                                "success": False, 
                                "message": "No data found", 
                                "data": []
                            }, 
                            status=status.HTTP_404_NOT_FOUND
                        )
            machineData = []
            machine_data = list(machine.values())
            for machine in machine_data:
                machineData.append({
                                "id": machine["machineType"],
                                "machineType": machine["machineType"],
                                "machineCount": machine["machineCount"]
                                }
                            )

            return Response(
                        {
                            "success": True, 
                            "message": "Data fetched successfully", 
                            "data": machineData
                        },
                        status=status.HTTP_200_OK
                    )
                    
    def post(self, request):
        machine_type = request.data["machineType"]
        machine_count = request.data["machineCount"]

        if not machine_type or machine_count is None:
            return Response(
                {"success": False, "message": "machineType and machineCount are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if machine_type not in dict(Machine.MACHINE_TYPES):
            return Response(
                {"success": False, "message": "Invalid machineType."},
                status=status.HTTP_400_BAD_REQUEST
            )

        machine, created = Machine.objects.update_or_create(
            machineType=machine_type, defaults={"machineCount": machine_count}
        )

        if created:
            return Response(
                {"success": True, "message": "Machine added successfully."},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"success": True, "message": "Machine count updated successfully."},
                status=status.HTTP_200_OK
            )

class MaterialView(APIView):
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
                material_data = {
                                "id": material_obj["materialType"],
                                "materialType": material_obj["materialType"],
                                "materialCount": material_obj["materialCount"]
                            }
                return Response(
                            {
                                "success": True, 
                                "message": "Data fetched successfully", 
                                "data": material_data
                            },
                            status=status.HTTP_200_OK
                        )
            else:
                return Response(
                            {
                                "success": False, 
                                "message": "No data found", 
                                "data": []
                            }, 
                            status=status.HTTP_404_NOT_FOUND
                        )
        else:
            # Fetch all material records
            material = Material.objects.all()
            if not material.exists():
                return Response(
                            {
                                "success": False, 
                                "message": "No data found", 
                                "data": []
                            }, 
                            status=status.HTTP_404_NOT_FOUND
                        )
            material_data = list(material.values())
            materialData = []
            for material in material_data:
                materialData.append(
                                        {
                                            "id": material["materialType"],
                                            "materialType": material["materialType"],
                                            "materialCount": material["materialCount"]
                                        }
                                    )
            return Response(
                        {
                            "success": True, 
                            "message": "Data fetched successfully", 
                            "data": materialData
                        },
                        status=status.HTTP_200_OK
                    )
    
    def post(self, request):
        material_type = request.data["materialType"]
        material_count = request.data["materialCount"]

        if not material_type or material_count is None:
            return Response(
                {"success": False, "message": "Material Type and Material Count are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if material_type not in dict(Material.MATERIAL_TYPES):
            return Response(
                {"success": False, "message": "Invalid materialType."},
                status=status.HTTP_400_BAD_REQUEST
            )

        material, created = Material.objects.update_or_create(
            materialType=material_type, defaults={"materialCount": material_count}
        )

        if created:
            return Response(
                {"success": True, "message": "material added successfully."},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"success": True, "message": "material count updated successfully."},
                status=status.HTTP_200_OK
            )

class RoadView(APIView):
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
                return Response(
                            {
                                "message": "Invalid Road Id", 
                                "success": False, 
                                "data": []
                            }, 
                            status=status.HTTP_400_BAD_REQUEST
                        )
            roadId = int(roadId)
            # Fetch road details for a specific road ID
            road_obj = Road.objects.filter(roadId=roadId).values().first()
            if road_obj:
                road = {
                        "id": road_obj["roadId"],
                        "roadId": road_obj["roadId"],
                        "areaCode": road_obj["areaCode_id"]
                    }
                return Response(
                            {
                                "success": True, 
                                "message": "Data fetched successfully", 
                                "data": road
                            },
                            status=status.HTTP_200_OK    
                        )
            else:
                return Response(
                            {
                                "success": False, 
                                "message": "No data found", 
                                "data": []
                            }, 
                            status=status.HTTP_404_NOT_FOUND
                        )
        else:
            # Fetch all road records
            roads = Road.objects.all()
            if not roads.exists():
                return Response(
                            {
                                "success": False, 
                                "message": "No data found", 
                                "data": []
                            }, 
                            status=status.HTTP_404_NOT_FOUND
                        )
            roadData = list()
            roads = list(roads.values())
            for road in roads:
                roadData.append(
                        {
                            "id": road["roadId"],
                            "roadId": road["roadId"],
                            "areaCode": road["areaCode_id"]
                        }
                    )
            return Response(
                        {
                            "success": True, 
                            "message": "Data fetched successfully", 
                            "data": roadData
                        },
                        status=status.HTTP_200_OK
                    )
    def post(self, request):
        """
        Handles POST request to add a new road.

        Parameters:
            request (HttpRequest): The HTTP request object containing road details.

        Returns:
            Response: JSON response indicating success or failure.
        """
        road_data = request.data
        
        # Validate input
        road_id = road_data.get("roadId")
        area_code = road_data.get("areaCode")
        
        if not road_id or not area_code:
            return Response(
                {"message": "roadId and areaCode are required", "success": False, "data": {}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not can_convert_to_int(road_id):
            return Response(
                {"message": "Invalid roadId", "success": False, "data": {}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not Area.objects.filter(areaCode=area_code).exists():
            return Response(
                {"message": "Invalid areaCode", "success": False, "data": {}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        road_id = int(road_id)
        
        if Road.objects.filter(roadId=road_id).exists():
            return Response(
                {"message": "roadId already exists", "success": False, "data": {}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create and save the new road entry
        road = Road(roadId=road_id, areaCode_id=area_code)
        road.save()
        
        return Response(
            {"success": True, "message": "Road added successfully", "data": {"roadId": road_id, "areaCode": area_code}},
            status=status.HTTP_201_CREATED
        )

class StreetLightView(APIView):
    def get(self, request, streetLightId=None):
        if streetLightId:
            response, status = getParticularStreetLight(streetLightId)
            return Response(response, status)
        else:
            response, status = getAllStreetLight()
            return Response(response, status)
    def post(self, request):
        street_light_data = request.data
        street_light_id = request.data["streetLightId"]
        area_code = request.data["areaCode"]
        lightStatus = request.data["status"]
        if not street_light_id or not area_code or not lightStatus:
            response = {"message": "streetLightId, lightstatus and areaCode are required", "success": False, "data": []}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        response, status = addStreetLight(street_light_id, area_code, lightStatus) 
        return Response(response, status)
        
        
class DrainageView(APIView):
    def get(self, request, drainageId=None):
        if drainageId:
            response, status = getParticularDrainage(drainageId)
            return Response(response, status)
        else:
            response, status = getAllDrainage()
            return Response(response, status)
    
    def post(self, request):
        drainage_id = request.data["drainageId"]
        area_code = request.data["areaCode"]
        drainageStatus = request.data["drainageStatus"]
        if not drainage_id or not area_code or not drainageStatus:
            response = {"message": "Drainage Id, Drainage Status and Area Code are required", "success": False, "data": []}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        response, status = addDrainage(drainage_id, area_code, drainageStatus)
        return Response(response, status)

class AreaView(APIView):
    def get(self, request, areaId=None):
        response, status = getArea(areaId)
        return Response(response, status)   

    def post(self, request):
        areaCode = request.data['areaCode']
        areaName = request.data['areaName']
        if not areaCode or not areaName:
            response = {"success": False,"message": "Both Area Code and Area Name should be present", "data": []}
            return Response(response,status=status.HTTP_400_BAD_REQUEST)
        response,http_status = createArea(areaCode, areaName)
        return Response(response,http_status)  