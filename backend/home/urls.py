from django.urls import path
from home.views import *

urlpatterns = [
    path("login",LoginView.as_view()),
    path("register",RegisterView.as_view()),
    path("createRequest",CreateRequestView.as_view()),
    path("request/", GetRequestsView.as_view()),  # Fetch all requests using ?areaCode=
    path("request/<int:requestId>/", GetRequestsView.as_view()),  # Fetch a specific request
    ]