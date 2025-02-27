# accounts/views.py

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
import jwt
import uuid
from datetime import datetime, timedelta
from .serializers import *
from django.conf import settings
from .models import *

class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate verification token
            token = jwt.encode({
                'user_id': str(user.id),
                'exp': datetime.utcnow() + timedelta(days=1)
            }, settings.SECRET_KEY, algorithm='HS256')
            
            # Send verification email
            verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
            print(f"Verification URL: {verification_url}")
            # send_mail(
            #     'Verify your email',
            #     f'Click here to verify your email: {verification_url}',
            #     settings.EMAIL_HOST_USER,
            #     [user.email]
            # )
            
            # Optionally auto-verify user for development
            user.is_verified = True
            user.save()
            
            return Response({
                'message': 'Registration successful. Please verify your email.',
                # 'verification_url': verification_url  # Only for development
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username_or_email = serializer.validated_data['username_or_email']
            password = serializer.validated_data['password']
            
            print(f"Attempting login with: {username_or_email}")  # Debug print
            
            # Check if the provided input is an email or username
            user = None
            if '@' in username_or_email:  # Check if it's an email
                try:
                    user = User.objects.get(email=username_or_email)
                    print(f"Found user by email: {user.username}")  # Debug print
                except User.DoesNotExist:
                    print("User not found with email")  # Debug print
                    return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            else:  # Else treat it as a username
                try:
                    user = User.objects.get(username=username_or_email)
                    print(f"Found user by username: {user.username}")  # Debug print
                except User.DoesNotExist:
                    print("User not found with username")  # Debug print
                    return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
                
                
            # Authenticate the user
            if user and user.check_password(password):
                print("Password check passed")
                if not user.is_verified:
                    return Response({
                        'message': 'Please verify your email first.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
                refresh = RefreshToken.for_user(user)
                return Response({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token)
                    })
            return Response({
                'message': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(email=serializer.validated_data['email'])
                
                # Generate reset token
                reset_token = str(uuid.uuid4())
                user.reset_password_token = reset_token
                user.save()
                
                # Send reset email
                reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
                send_mail(
                    'Reset your password',
                    f'Click here to reset your password: {reset_url}',
                    settings.EMAIL_HOST_USER,
                    [user.email]
                )
                
                return Response({
                    'message': 'Password reset instructions sent to your email.'
                })
            except User.DoesNotExist:
                return Response({
                    'message': 'User with this email does not exist.'
                }, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(reset_password_token=serializer.validated_data['token'])
                user.set_password(serializer.validated_data['new_password'])
                user.reset_password_token = None
                user.save()
                
                return Response({
                    'message': 'Password reset successful.'
                })
            except User.DoesNotExist:
                return Response({
                    'message': 'Invalid reset token.'
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)