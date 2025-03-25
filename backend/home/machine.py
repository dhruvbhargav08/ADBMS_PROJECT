from rest_framework.views import APIView, Response
from home.models import *
from rest_framework import status  
from home.utils import *

def getParticularMachine(machineType):
    obj = Machine.objects.filter(machineType=machineType)
    if obj:
        obj = obj[0]
        data = {"id": obj.machineType, "machineType": obj.machineType, "machineCount": obj.machineCount}
        response = {"success": True, "message": "Data fetched successfully", "data":data}
        return response, status.HTTP_200_OK
    else:
        response = {"success": False, "message": "No data found", "data": []}
        return response, status.HTTP_200_OK

def getAllMachine():
    objs = Machine.objects.filter()
    if not objs.exists():
        response = {"success": False, "message": "No data found",  "data": []}
        return response, status.HTTP_200_OK
    data = []
    for obj in objs:
        data.append({"id": obj.machineType, "machineType": obj.machineType, "machineCount": obj.machineCount })
    response = {
                    "success": True, 
                    "message": "Data fetched successfully", 
                    "data": data
                }
    return response, status.HTTP_200_OK

def addMachine(machine_type, machine_count):
    if machine_type not in dict(Machine.MACHINE_TYPES):
        response = {"success": False, "message": "Invalid machineType.", "data": []}
        return response,tatus.HTTP_200_OK
    machine, created = Machine.objects.update_or_create(machineType=machine_type, defaults={"machineCount": machine_count})
    if created:
        data, _ = getAllMachine()
        response = {"success": True, "message": "Machine added successfully.", "data": data["data"]}
        return response, status.HTTP_201_CREATED
    else:
        data, _ = getAllMachine()
        response = {"success": True, "message": "Machine count updated successfully.", "data": data["data"]}
        return response, status.HTTP_200_OK