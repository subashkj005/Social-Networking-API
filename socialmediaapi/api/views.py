from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from api.serializers import UsersSerializer, LoginSerializer
from .models import Users


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
            return Response(serializer.data, status=status.HTTP_201_CREATED)

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
