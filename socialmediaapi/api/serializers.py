from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import Users, Requests, Connections


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
        
        if not name.isalpha():
            raise serializers.ValidationError("Name must contain only alphabets")
        
        user = Users.objects.create(name=name, email=email)
        user.set_password(password)
        user.save()
        return user
    
    
class UserRequestsSerializer(serializers.ModelSerializer):
    requested_by = UsersSerializer(read_only=True)

    class Meta:
        model = Requests
        fields = ['id', 'requested_by', 'status', 'requested_at']
        
        
class UserConnectionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Connections
        fields = ['user', 'friend']

        
    
    
