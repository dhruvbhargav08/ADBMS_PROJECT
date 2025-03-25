from rest_framework.views import APIView, Response
from home.models import *
from rest_framework import status  
from home.utils import *

def getParticularWorker(workerType):
    obj = ManPower.objects.filter(workerType=workerType)
    if obj:
        obj = obj[0]
        data = {"id": obj.workerType, "workerType": obj.workerType, "workerCount": obj.workerCount}
        response = {"success": True, "message": "Data fetched successfully", "data": data}
        return response, status.HTTP_200_OK
    else:
        response = {"success": False, "message": "No data found", "data": []}
        return response, status.HTTP_200_OK

def getAllWorker():
    objs = ManPower.objects.filter()
    if not objs.exists():
        response = {"success": False, "message": "No data found", "data": []}
        return response, status.HTTP_200_OK
    data = list()
    for obj in objs:
        data.append(
                        {
                            "id": obj.workerType,
                            "workerType": obj.workerType,
                            "workerCount": obj.workerCount
                        }
                    )
    response = {"success": True, "message": "Data fetched successfully", "data": data}
    return response, status.HTTP_200_OK

def addWorker(worker_type, worker_count):
    if worker_type not in dict(ManPower.WORKER_TYPES):
        response =  {"success": False, "message": "Invalid workerType.", "data": []}
        return response, status.HTTP_200_OK
    manpower, created = ManPower.objects.update_or_create(workerType=worker_type, defaults={"workerCount": worker_count})
    if created:
        data, _ = getAllWorker()
        response = {"success": True, "message": "Worker added successfully.","data": data["data"]}
        return response, status.HTTP_201_CREATED
    else:
        data, _ = getAllWorker()
        response = {"success": True, "message": "Worker count updated successfully.","data": data["data"]}
        return response, status.HTTP_200_OK