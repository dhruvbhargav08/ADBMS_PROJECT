from rest_framework.views import APIView, Response
from home.models import *
from rest_framework import status  
from home.utils import *

def getParticularRoad(roadId):
    data = dict()
    if not can_convert_to_int(roadId):
        response = {"message": "Invalid Road Id", "success": False, "data": []}
        return response, status.HTTP_200_OK
    roadId = int(roadId)
    obj = Road.objects.filter(roadId=roadId)
    if obj:
        obj = obj[0]
        data = {"id": obj.roadId, "roadId":obj.roadId, "areaCode":obj.areaCode_id}
        response = {"success": True, "message": "Data fetched successfully", "data": data}
        return response, status.HTTP_200_OK    
    else:
        response = {"success": False, "message": "No data found", "data": []}
        return response, status.HTTP_200_OK

def getAllRoad():
    data = list()
    objs = Road.objects.filter()
    if not objs.exists():
        response = {"success": False, "message": "No data found", "data": []}
        return response, status.HTTP_200_OK
    for obj in objs:
        data.append({"id": obj.roadId, "roadId": obj.roadId, "areaCode": obj.areaCode_id})
    response = {"success": True, "message": "Data fetched successfully", "data": data}
    return response, status.HTTP_200_OK

def addRoad(road_id, areaCode):
    if not can_convert_to_int(road_id):
        response = {"message": "Invalid roadId", "success": False, "data": []}
        return response, status.HTTP_200_OK
    if not Area.objects.filter(areaCode=areaCode).exists():
        response = {"message": "Invalid areaCode", "success": False, "data": []}
        return response,  status.HTTP_200_OK
    road_id = int(road_id)
    if Road.objects.filter(roadId=road_id).exists():
        response = {"message": "roadId already exists", "success": False, "data": []}
        return response, status.HTTP_200_OK
    Road.objects.create(roadId=road_id, areaCode_id=areaCode)
    data, _ = getParticularRoad(road_id)
    response = {"success": True, "message": "Road added successfully", "data": data["data"]}
    return response, status.HTTP_201_CREATED