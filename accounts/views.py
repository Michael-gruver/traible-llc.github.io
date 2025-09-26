# accounts/views.py

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.core.cache import cache
from django.utils import timezone
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import jwt
import uuid
import logging
from datetime import datetime, timedelta
from .serializers import *
from django.conf import settings
from .models import *

logger = logging.getLogger(__name__)

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
            
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Registration successful.',
                'refresh': str(refresh),
                'access': str(refresh.access_token)
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


class PasswordResetRequestView(APIView):
    """
    Request password reset - sends email with reset link
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        
        # Rate limiting check
        cache_key = f"password_reset_request_{email}"
        if cache.get(cache_key):
            logger.warning(f"Rate limit exceeded for password reset request: {email}")
            return Response({
                'message': 'If an account with this email exists, you will receive reset instructions.'
            }, status=status.HTTP_200_OK)
        
        try:
            user = User.objects.get(email=email)
            
            # Check if user can request password reset
            if not user.can_request_password_reset():
                logger.warning(f"Password reset rate limit exceeded for user: {email}")
                return Response({
                    'message': 'If an account with this email exists, you will receive reset instructions.'
                }, status=status.HTTP_200_OK)
            
            # Generate secure reset token
            token, uid = user.generate_password_reset_token()
            
            # Create reset URL
            reset_url = f"{settings.FRONTEND_URL}/password-reset-confirm?token={token}&uid={uid}"
            
            # Send email
            try:
                self._send_password_reset_email(user.email, reset_url, user.username)
                logger.info(f"Password reset email sent to: {email}")
            except Exception as e:
                logger.error(f"Failed to send password reset email to {email}: {str(e)}")
                # Don't fail the request if email sending fails
            
            # Increment attempts counter
            user.increment_password_reset_attempts()
            
        except User.DoesNotExist:
            # Don't reveal if email exists for security
            logger.info(f"Password reset requested for non-existent email: {email}")
        
        # Set rate limit (1 hour)
        cache.set(cache_key, True, 3600)
        
        return Response({
            'message': 'If an account with this email exists, you will receive reset instructions.'
        }, status=status.HTTP_200_OK)
    
    def _send_password_reset_email(self, email, reset_url, username):
        """Send password reset email"""
        subject = 'Password Reset Request - Traible'
        
        # Create HTML email content
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Password Reset Request</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #88A0C2;">Traible</h1>
                    <p style="color: #666;">Know Your Tribe</p>
                </div>
                
                <h2>Password Reset Request</h2>
                
                <p>Hello {username},</p>
                
                <p>We received a request to reset your password for your Traible account. If you made this request, click the button below to reset your password:</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" 
                       style="background-color: #88A0C2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Reset Password
                    </a>
                </div>
                
                <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #88A0C2;">{reset_url}</p>
                
                <p><strong>Important:</strong></p>
                <ul>
                    <li>This link will expire in 1 hour</li>
                    <li>This link can only be used once</li>
                    <li>If you didn't request this password reset, please ignore this email</li>
                </ul>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                
                <p style="font-size: 12px; color: #666;">
                    This email was sent from Traible. If you have any questions, please contact our support team.
                </p>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text_message = f"""
        Password Reset Request - Traible
        
        Hello {username},
        
        We received a request to reset your password for your Traible account. If you made this request, click the link below to reset your password:
        
        {reset_url}
        
        Important:
        - This link will expire in 1 hour
        - This link can only be used once
        - If you didn't request this password reset, please ignore this email
        
        This email was sent from Traible. If you have any questions, please contact our support team.
        """
        
        send_mail(
            subject=subject,
            message=text_message,
            html_message=html_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )


class PasswordResetValidateView(APIView):
    """
    Validate password reset token
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetValidateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        token = serializer.validated_data['token']
        uid = serializer.validated_data['uid']
        
        try:
            user = User.objects.get(id=uid)
            if user.validate_password_reset_token(token):
                return Response({
                    'valid': True,
                    'message': 'Token is valid'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'valid': False,
                    'message': 'Invalid or expired token'
                }, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({
                'valid': False,
                'message': 'Invalid or expired token'
            }, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """
    Confirm password reset with new password
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        token = serializer.validated_data['token']
        uid = serializer.validated_data['uid']
        password = serializer.validated_data['password']
        
        try:
            user = User.objects.get(id=uid)
            
            # Validate token
            if not user.validate_password_reset_token(token):
                logger.warning(f"Invalid password reset token used for user: {user.email}")
                return Response({
                    'message': 'Invalid or expired token'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Set new password
            user.set_password(password)
            user.save()
            
            # Invalidate the token (single use)
            user.invalidate_password_reset_token(token)
            
            # Reset password reset attempts
            user.reset_password_attempts()
            
            # Invalidate all user sessions (optional security measure)
            # You can implement this if you're tracking user sessions
            
            logger.info(f"Password successfully reset for user: {user.email}")
            
            return Response({
                'message': 'Password has been reset successfully'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            logger.warning(f"Password reset attempted for non-existent user ID: {uid}")
            return Response({
                'message': 'Invalid user'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error during password reset confirmation: {str(e)}")
            return Response({
                'message': 'An error occurred while resetting your password'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)