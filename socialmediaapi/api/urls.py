from django.urls import path
from api import views


urlpatterns = [
    path('auth/register/', views.UserRegisterAPIView.as_view(), name='register_user' ),
    path('auth/login/', views.LoginUserAPIView.as_view(), name='login' ),
    path('users/search/', views.SearchUsersListView.as_view(), name='search_users'),
    path('users/send_request/', views.SendFriendRequestAPIView.as_view(), name='send_request'),
]