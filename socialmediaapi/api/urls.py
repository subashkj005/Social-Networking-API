from django.urls import path
from api import views


urlpatterns = [
    # Authentication
    path('auth/register/', views.UserRegisterAPIView.as_view(), name='register_user' ),
    path('auth/login/', views.LoginUserAPIView.as_view(), name='login' ),
    # Users
    path('users/search/', views.SearchUsersListView.as_view(), name='search_users'),\
    # Requests
    path('requests/send_request/', views.SendFriendRequestAPIView.as_view(), name='send_request'),
    path('requests/update/', views.UpdateFriendRequestAPIView.as_view(), name='send_request'),
    path('requests/pending_requests/', views.ListPendingRequests.as_view(), name='send_request'),
    path('requests/list_friends/', views.ListFriends.as_view(), name='list_friends'),
]