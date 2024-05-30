from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import Users


class UsersSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(max_length=255, write_only=True)
    
    class Meta:
        model = Users
        fields = ['name', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}
        
    def create(self, validated_data):
        name = validated_data.get('name', None)
        email = validated_data.get('email', None)
        password = validated_data.get('password', None)
        
        if name is None or email is None or password is None:
            raise serializers.ValidationError("Missing required fields")
        
        user = Users.objects.create(name=name, email=email)
        user.set_password(password)
        user.save()
        return user
    
    
class LoginSerializer(serializers.Serializer):
    
    id = serializers.UUIDField(read_only=True)
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255, write_only=True)
    
    def validate(self, validated_data):

        email = validated_data.get('email', None)
        password = validated_data.get('password', None)
        
        if email is None:
            raise serializers.ValidationError('Email Address is required')
        if password is None:
            raise serializers.ValidationError('Password is required')
        
        
        user = authenticate(email=email, password=password)
        
        print('user = ', user)
        print('type user = ', type(user))
        

        if user is None:
            raise serializers.ValidationError('Invalid login credentials')
        
        if user is None:
            raise serializers.ValidationError("Invalid email or password")
        
        return user