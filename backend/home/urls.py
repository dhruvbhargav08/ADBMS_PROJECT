from django.urls import path
from home.views import *

urlpatterns = [
    path("login",LoginView.as_view()),
    path("register",RegisterView.as_view()),
    path("requests",RequestView.as_view()),
    path("requests", RequestView.as_view()),  
    path("requests/<str:requestId>", RequestView.as_view()),
    path("manpowers",GetManpower.as_view()),
    path("manpowers/<str:workerType>",GetManpower.as_view()),
    path("machines",GetMachine.as_view()),
    path("machines/<str:machineType>",GetMachine.as_view()),
    path("materials",GetMaterial.as_view()),
    path("materials/<str:materialType>",GetMaterial.as_view()),
    path("roads",GetRoad.as_view()),
    path("roads/<str:roadId>",GetRoad.as_view()),
    path("streetlights",GetStreetLight.as_view()),
    path("streetlights/<str:streetLightId>",GetStreetLight.as_view()),
    path("drains",GetDrainage.as_view()),
    path("drains/<str:drainageId>",GetDrainage.as_view()),
    ]