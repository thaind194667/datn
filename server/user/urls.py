from .views import LoginApi, registerApi
from django.urls import path

urlpatterns = [
    path("login/", LoginApi.as_view()),
    path("register/", registerApi.as_view()),
]