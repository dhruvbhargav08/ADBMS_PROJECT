from rest_framework.views import APIView, Response
from home.models import *
from rest_framework import status  
from home.utils import *

def getParticularDrainage(drainageId):
    data = list()
    if not can_convert_to_int(drainageId):
        response = {"message": "Invalid Drainage Id", "success": False, "data": data}
        return response, status.HTTP_400_BAD_REQUEST
    drainageId = int(drainageId)
    objs = Drainage.objects.filter(drainageId=drainageId)
    for obj in objs:
        data.append({"id": obj.drainageId, "drainageId": obj.drainageId, "areaCode": obj.areaCode_id, "status": obj.status})
    if data:
        response = {"success": True, "message": "Data fetched successfully", "data": data}
        return response, status.HTTP_200_OK
    else:
        response = {"success": True, "message": "No data found", "data": data}
        return response, status.HTTP_404_NOT_FOUND

def getAllDrainage():
    data = list()
    objs = Drainage.objects.filter()
    if not objs.exists():
        response = {"success": False, "message": "No data found", "data": data}
        return response, status.HTTP_404_NOT_FOUND  
    for obj in objs:
        data.append({"id": obj.drainageId, "drainageId": obj.drainageId, "areaCode": obj.areaCode_id, "status": obj.status})
    response = {"success": True, "message": "Data fetched successfully", "data": data}
    return response, status.HTTP_200_OK

def addDrainage(drainage_id, area_code, drainageStatus):
    if not can_convert_to_int(drainage_id):
        response = {"message": "Invalid drainageId", "success": False, "data": []}
        return response, status.HTTP_400_BAD_REQUEST
    
    if not Area.objects.filter(areaCode=area_code).exists():
        response = {"message": "Invalid areaCode", "success": False, "data": []}
        return response, status.HTTP_400_BAD_REQUEST
    
    drainage_id = int(drainage_id)
    if Drainage.objects.filter(drainageId=drainage_id).exists():
        response = {"message": "drainageId already exists", "success": False, "data": []}
        return response, status.HTTP_400_BAD_REQUEST

    Drainage.objects.create(drainageId=drainage_id, areaCode_id=area_code, status=drainageStatus)
    data, _ = getAllDrainage()
    response = {"success": True, "message": "Drainage added successfully", "data": data["data"]}
    return response, status.HTTP_201_CREATED