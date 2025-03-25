from rest_framework.views import APIView, Response
from home.models import *
from rest_framework import status  
from home.utils import *

def createArea(areaCode, areaName):
    if Area.objects.filter(areaCode=areaCode).exists():
        response = {"success": False,"message": "Area already exists"}
        return response, status.HTTP_400_BAD_REQUEST
    Area.objects.create(areaCode=areaCode, areaName=areaName)
    data, _ = getParticularArea(areaCode)
    response = {"success": True, "message": "Area added successfully", "data": data["data"]}
    return response, status.HTTP_200_OK

def getParticularArea(areaCode):
    data = list()
    obj = Area.objects.filter(areaCode=areaCode)
    if not obj.exists():
        response = {"success": False, "message": "Area does not exist", "data": data}
        return response, status.HTTP_200_OK
    obj = obj[0]
    data = {"id": obj.areaCode, "areaCode": obj.areaCode, "areaName": obj.areaName}
    response = {"success": True, "message": "Data fetched successfully", "data": data}
    return response, status.HTTP_200_OK

def getAllArea():
    data = list()
    objs = Area.objects.filter()
    for obj in objs:
        data.append({"id": obj.areaCode, "areaCode": obj.areaCode, "areaName": obj.areaName})
    response = {"success": True, "message": "Data fetched successfully", "data": data}
    return response, status.HTTP_200_OK

def getArea(areaId):
    if areaId:
        if not can_convert_to_int(areaId):
            response = {"message": "Invalid Area Id", "success": False}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        areaId = int(areaId)
        response, status = getParticularArea(areaId)
        return response, status
    else:
        response, status = getAllArea()
        return response, status