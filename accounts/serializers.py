# accounts/serializers.py

from rest_framework import serializers
from .models import *
import re

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'is_verified')
        read_only_fields = ('id', 'is_verified')

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'confirm_password')
        extra_kwargs = {
            'email': {'validators': []},  # Remove default unique validator
            'username': {'validators': []}  # Remove default unique validator
        }

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        
        # ✅ Password strength validation
        password = data['password']
        if len(password) < 8:
            raise serializers.ValidationError({"error": "Password must be at least 8 characters long."})
        if not any(char.isupper() for char in password):
            raise serializers.ValidationError({"error": "Password must contain at least one uppercase letter."})
        if not any(char.islower() for char in password):
            raise serializers.ValidationError({"error": "Password must contain at least one lowercase letter."})
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise serializers.ValidationError({"error": "Password must contain at least one special character."})
        
        # Check email and username together
        email_exists = User.objects.filter(email=data['email']).exists()
        username_exists = User.objects.filter(username=data['username']).exists()
        
        errors = {}
        if email_exists or username_exists:
            if email_exists:
                errors = 'This email is already registered'
            if username_exists:
                errors = 'This username is already taken'
            raise serializers.ValidationError({
                'error': errors
            })
        
        return data

    def create(self, validated_data):
        try:
            validated_data.pop('confirm_password')
            user = User.objects.create_user(**validated_data)
            return user
        except Exception as e:
            raise serializers.ValidationError({
                "message": "Error creating user",
                "details": str(e)
            })

class LoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField()
    password = serializers.CharField(write_only=True)

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetValidateSerializer(serializers.Serializer):
    token = serializers.CharField()
    uid = serializers.CharField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    uid = serializers.CharField()
    password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        
        # Password strength validation
        password = data['password']
        if len(password) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        if not any(char.isupper() for char in password):
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in password):
            raise serializers.ValidationError("Password must contain at least one lowercase letter")
        if not any(char.isdigit() for char in password):
            raise serializers.ValidationError("Password must contain at least one number")
        
        # Check for common patterns
        if re.search(r'(.)\1{2,}', password):
            raise serializers.ValidationError("Password cannot contain more than 2 consecutive identical characters")
        
        # Check for sequential numbers
        if re.search(r'123|234|345|456|567|678|789|890', password):
            raise serializers.ValidationError("Password cannot contain sequential numbers")
        
        # Check for sequential letters
        if re.search(r'abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz', password.lower()):
            raise serializers.ValidationError("Password cannot contain sequential letters")
        
        return data

# Keep old serializers for backward compatibility
class ForgotPasswordSerializer(PasswordResetRequestSerializer):
    pass

class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return data