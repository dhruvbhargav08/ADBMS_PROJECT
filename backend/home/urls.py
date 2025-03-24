from django.urls import path
from home.views import *

urlpatterns = [
    path("login",LoginView.as_view()),
    path("register",RegisterView.as_view()),
    path("requests",RequestView.as_view()),
    path("requests", RequestView.as_view()),  
    path("requests/<str:requestId>", RequestView.as_view()),
    path("manpowers",ManpowerView.as_view()),
    path("manpowers/<str:workerType>",ManpowerView.as_view()),
    path("machines",MachineView.as_view()),
    path("machines/<str:machineType>",MachineView.as_view()),
    path("materials",MaterialView.as_view()),
    path("materials/<str:materialType>",MaterialView.as_view()),
    path("roads",RoadView.as_view()),
    path("roads/<str:roadId>",RoadView.as_view()),
    path("streetlights",StreetLightView.as_view()),
    path("streetlights/<str:streetLightId>",StreetLightView.as_view()),
    path("drains",DrainageView.as_view()),
    path("drains/<str:drainageId>",DrainageView.as_view()),
    path("areas",AreaView.as_view()),
    path("areas/<str:areaId>",AreaView.as_view()),
    ]