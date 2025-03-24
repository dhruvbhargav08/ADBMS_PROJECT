from rest_framework.views import APIView, Response
from home.models import *
from rest_framework import status  
from home.utils import *

def getParticularStreetLight(streetLightId):
    data = list()
    if not can_convert_to_int(streetLightId):
        response = {"message": "Invalid Street Light Id", "success": False, "data": data}
        return response, status.HTTP_400_BAD_REQUEST
    streetLightId = int(streetLightId)
    objs = StreetLight.objects.filter(streetLightId=streetLightId)
    for obj in objs:
        data.append({"id": obj.streetLightId, "streetLightId": obj.streetLightId, "areaCode": obj.areaCode_id, "status": obj.status})
    if data:
        response = {"success": True, "message": "Data fetched successfully", "data": data}
        return response, status.HTTP_200_OK
    else:
        response = {"success": False, "message": "No data found", "data": data}
        return response, status.HTTP_404_NOT_FOUND

def getAllStreetLight():
    data = list()
    objs = StreetLight.objects.filter()
    if not objs.exists():
        response = {"success": False, "message": "No data found", "data": data}
        return response, status.HTTP_404_NOT_FOUND
    for obj in objs:
        data.append({"id": obj.streetLightId, "streetLightId": obj.streetLightId, "areaCode": obj.areaCode_id, "status": obj.status})
    response = {"success": True, "message": "Data fetched successfully", "data": data}
    return response, status.HTTP_200_OK

def addStreetLight(street_light_id, area_code, lightStatus):
    data = list()
    if not can_convert_to_int(street_light_id):
        response = {"message": "Invalid streetLightId", "success": False, "data": data}
        return response, status.HTTP_400_BAD_REQUEST

    if not Area.objects.filter(areaCode=area_code).exists():
        response = {"message": "Invalid areaCode", "success": False, "data": data}
        return response, status.HTTP_400_BAD_REQUEST

    street_light_id = int(street_light_id)
    if StreetLight.objects.filter(streetLightId=street_light_id).exists():
        response = {"message": "streetLightId already exists", "success": False, "data": data}
        return response, status.HTTP_400_BAD_REQUEST
    StreetLight.objects.create(streetLightId=street_light_id, areaCode_id=area_code, status=lightStatus)
    data, _ = getAllStreetLight()
    response = {"success": True, "message": "Street Light added successfully", "data": data["data"]}
    return response, status.HTTP_201_CREATED