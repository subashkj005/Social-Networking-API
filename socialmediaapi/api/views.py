from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework_simplejwt.tokens import RefreshToken
from api.serializers import UsersSerializer, UserRequestsSerializer
from api.paginations import CustomPagination
from api.utils import has_reached_request_limit, is_password_strong_enough
from api.models import Users, Requests


class UserRegisterAPIView(APIView):
    """
    API endpoint to register a new user.

    Accepts POST requests with user data including name, email, password, and confirm-password.
    
    Methods:
        post(request): Handles the HTTP POST request to register a user.

    Returns:
            Response: A Response object with appropriate status and message.
                - 201 Created: If the user is successfully registered.
                - 400 Bad Request: If there are validation errors in the user data.
                - 409 Conflict: If the email is already registered.
                - 422 Unprocessable Entity: If the provided data is invalid.
    """
    permission_classes = []

    def post(self, request):
        data = request.data

        if not data:
            return Response({'message': "Invalid data"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        if not is_password_strong_enough(data['password']):
            return Response({'message': "Password is not strong enough"}, status=status.HTTP_400_BAD_REQUEST)

        user_exists = Users.objects.filter(email=data['email']).first()
        if user_exists:
            return Response({'message': 'Email already registered'}, status=status.HTTP_409_CONFLICT)

        if data['password'] != data['confirm-password']:
            return Response({'message': "Passwords doesn't match"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UsersSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': "User registered successfully"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginUserAPIView(APIView):
    """
    API view for logging in a user.
    
    Accepts POST request to authenticate the user with the provided email and password.
    
    Methods:
        post(request): Handles the HTTP POST request to authenticate a user.
    
    Returns:
            Response: 
                - 200 OK: If the login is successful, returns authentication tokens.
                - 400 Bad Request: If there are validation errors in the login data or invalid credentials.
    """
    permission_classes = []

    def post(self, request):
        email = request.data.get('email', None)
        password = request.data.get('password', None)

        if email is None:
            return Response({'message': "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        if password is None:
            return Response({'message': "Password is required"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(email=email, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({'message': 'Login Successfull',
                             'refresh': str(refresh),
                             'access': str(refresh.access_token),
                             }, status=status.HTTP_200_OK)
        return Response({'message': "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)


class SearchUsersListView(generics.ListAPIView):
    """
    API view for searching and listing users.

    Accepts GET request to search for users based on a keyword provided as a query parameter.
    The search is performed on either the user's name or email, depending on the nature of the keyword.

    Methods:
        get_queryset(): Retrieves the queryset of users matching the search keyword.
    
    Returns:
        List : A list of users matching the search criteria or an empty list if no keyword is provided.
    """
    serializer_class = UsersSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        keyword = self.request.query_params.get('keyword', None)

        if keyword is not None:
            if keyword.isalpha():
                queryset = Users.objects.filter(name__icontains=keyword)
            else:
                queryset = Users.objects.filter(email__icontains=keyword)
            return queryset
        return []


class SendFriendRequestAPIView(APIView):
    """
    API view for sending a friend request.

    Accepts POST request to send a friend request to a user specified by their email.
    
    Methods:
        post(request): Handles the HTTP POST request to send a friend request.
    
    Returns:
        Response: 
            - 201 Created: If the friend request is sent successfully.
            - 400 Bad Request: If there are validation errors, the user doesn't exist, the request already exists, 
              or the maximum requests per minute are reached.
    """
    
    def post(self, request):
        email = request.data.get('email', None)
        sender = request.user

        try:
            recipient = Users.objects.get(email=email)
        except Users.DoesNotExist:
            return Response({'message': "User doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)

        request_already_exists = Requests.objects.filter(
            requested_by=sender, requested_to=recipient).first()
        if request_already_exists:
            return Response({'message': "Request already exists"}, status=status.HTTP_400_BAD_REQUEST)

        if has_reached_request_limit(sender):
            return Response({'message': 'Maximum requests per minute reached. Please wait a while before sending more.'},
                            status=status.HTTP_400_BAD_REQUEST)
            
        new_request = Requests.objects.create(requested_by=sender,
                                              requested_to=recipient)

        return Response({'message': "Friend request sent successfully"}, status=status.HTTP_201_CREATED)
        


class UpdateFriendRequestAPIView(APIView):
    """
    API view for updating the status of a friend request.

    Accepts POST request to either accept or reject a friend request based on the provided task.

    Methods:
        post(request): Handles the HTTP POST request to update the status of a friend request.

    Returns:
        Response:
            - 200 OK: If the request status is updated successfully.
            - 400 Bad Request: If there are validation errors, missing fields, invalid request ID, 
              the request doesn't exist, or the user doesn't have permission to update the request.
    """
    def post(self, request):
        task = request.data.get('task', None)
        request_id = request.data.get('request_id', None)
        update_requested_user = request.user

        if task is None or request_id is None:
            return Response({'message': "Required fields missing"})
        
        values =  Requests.objects.filter(requested_to=self.request.user,
                                       status='accepted').order_by('-requested_at')
        
        print('Friends = ', values)

        try:
            user_request = Requests.objects.get(id=request_id)
        except Requests.DoesNotExist:
            return Response({'message': "Request doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError:
            return Response({'message': "Invalid request ID."}, status=status.HTTP_400_BAD_REQUEST)

        if user_request.requested_to.id == update_requested_user.id:

            if task == 'accept':
                request_serializer = UserRequestsSerializer(
                    user_request, data={'status': 'accepted'}, partial=True)
                if request_serializer.is_valid():
                    request_serializer.save()
                    return Response({'message': "Request accepted Successfully"},
                                    status=status.HTTP_200_OK)

                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            elif task == 'reject':
                serializer = UserRequestsSerializer(
                    user_request, data={'status': 'rejected'}, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({'message': "Request rejected Successfully"}, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': "Invalid field values"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': "You do not have permission to perform this action."},
                        status=status.HTTP_400_BAD_REQUEST)


class ListPendingRequests(generics.ListAPIView):
    """
    API view for listing pending friend requests.

    This view retrieves and paginates all pending friend requests for the authenticated user.

    Methods:
        get_queryset(): Retrieves the queryset of pending friend requests for the authenticated user.
    
    Returns:
        List: A list of pending friend requests for the authenticated user.
    """
    serializer_class = UserRequestsSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return Requests.objects.filter(requested_to=self.request.user,
                                       status='pending').order_by('-requested_at')


class ListFriends(generics.ListAPIView):
    """
    API view for listing accepted friend requests.

    This view retrieves and paginates all accepted friend requests for the authenticated user.

    Methods:
        get_queryset(): Retrieves the queryset of accepted friend requests for the authenticated user.
    
    Returns:
        QuerySet: A queryset of accepted friend requests for the authenticated user.
    """
    serializer_class = UserRequestsSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return Requests.objects.filter(requested_to=self.request.user,
                                       status='accepted').order_by('-requested_at')
