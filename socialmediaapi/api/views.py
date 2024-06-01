from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework_simplejwt.tokens import RefreshToken
from api.serializers import UsersSerializer, UserRequestsSerializer, UserConnectionSerializer
from api.paginations import CustomPagination
from .models import Users, Requests, Connections


class UserRegisterAPIView(APIView):
    permission_classes = []

    def post(self, request):
        data = request.data

        if not data:
            return Response({'message': "Invalid data"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

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

        current_time = timezone.now()
        min_time = current_time - timedelta(minutes=1)

        total_requests_in_last_minute = Requests.objects.filter(
            requested_at__gte=min_time, requested_at__lte=current_time, requested_by=sender)

        if total_requests_in_last_minute.count() >= 3:
            return Response({'message': 'Maximum requests per minute reached. Please wait a while before sending more.'},
                            status=status.HTTP_400_BAD_REQUEST)

        data = {
            'requested_by': sender.id,
            'requested_to': recipient.id
        }
        serializer = UserRequestsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': "Friend request sent successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateFriendRequestAPIView(APIView):
    def post(self, request):
        task = request.data.get('task', None)
        request_id = request.data.get('request_id', None)
        update_requested_user = request.user

        if task is None or request_id is None:
            return Response({'message': "Required fields missing"})

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

                data = {
                    'user': update_requested_user.id,
                    'friend': user_request.requested_by.id
                }
                connection_serializer = UserConnectionSerializer(data=data)
                if connection_serializer.is_valid():
                    connection_serializer.save()

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
    serializer_class = UserRequestsSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return Requests.objects.filter(requested_to=self.request.user,
                                       status='pending')


class ListFriends(generics.ListAPIView):
    serializer_class = UserRequestsSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return Requests.objects.filter(requested_by=self.request.user,
                                       status='accepted')
