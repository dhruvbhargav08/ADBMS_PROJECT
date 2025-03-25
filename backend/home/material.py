from rest_framework.views import APIView, Response
from home.models import *
from rest_framework import status  
from home.utils import *

def getParticularMaterial(materialType):
    obj = Material.objects.filter(materialType=materialType)
    if obj:
        obj = obj[0]
        data = {"id": obj.materialType, "materialType": obj.materialType, "materialCount": obj.materialCount}
        response = {"success": True, "message": "Data fetched successfully", "data": data}
        return response, status.HTTP_200_OK
    else:
        response = {"success": False, "message": "No data found", "data": []}
        return response, status.HTTP_200_OK

def getAllMaterial():
    data = list()
    objs = Material.objects.filter()
    if not objs.exists():
        response = {"success": False, "message": "No data found", "data": []}
        return response, status.HTTP_200_OK
    for obj in objs:
        data.append({"id": obj.materialType, "materialType": obj.materialType, "materialCount": obj.materialCount})
    response = {"success": True, "message": "Data fetched successfully", "data": data}
    return response, status.HTTP_200_OK

def addMaterial(material_type, material_count):
    if material_type not in dict(Material.MATERIAL_TYPES):
        response = {"success": False, "message": "Invalid materialType.", "data": []}
        return response, status.HTTP_200_OK
    material, created = Material.objects.update_or_create(materialType=material_type, defaults={"materialCount": material_count})
    if created: 
        data , _ = getAllMaterial()
        response = {"success": True, "message": "material added successfully." ,"data": data["data"]}
        return  response, status.HTTP_201_CREATED
    else:
        data , _ = getAllMaterial()
        response = {"success": True, "message": "material count updated successfully.", "data": data["data"]}
        return response, status.HTTP_200_OK
