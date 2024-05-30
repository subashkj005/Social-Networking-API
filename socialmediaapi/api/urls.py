from django.urls import path
from .views import UserRegisterAPIView, LoginUserAPIView


urlpatterns = [
    path('auth/register/', UserRegisterAPIView.as_view(), name='register_user' ),
    path('auth/login/', LoginUserAPIView.as_view(), name='login' ),
]