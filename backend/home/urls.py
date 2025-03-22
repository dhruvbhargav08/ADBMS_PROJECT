from django.urls import path
from home.views import *

urlpatterns = [
    path("login",LoginView.as_view()),
    path("register",RegisterView.as_view()),
    path("requests",RequestView.as_view()),
    path("requests", RequestView.as_view()),  
    path("requests/<int:requestId>", RequestView.as_view())
    ]