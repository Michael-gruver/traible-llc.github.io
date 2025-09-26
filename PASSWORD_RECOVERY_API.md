# Password Recovery System API Specification

This document outlines the backend API endpoints required for the secure password recovery system.

## Overview

The password recovery system consists of three main endpoints:
1. **Password Reset Request** - Initiates the password reset process
2. **Password Reset Validation** - Validates the reset token
3. **Password Reset Confirmation** - Completes the password reset

## Security Features

- **Rate Limiting**: Prevent brute force attacks
- **Token Expiration**: Reset tokens expire after 1 hour
- **Single Use Tokens**: Tokens are invalidated after use
- **Secure Token Generation**: Cryptographically secure random tokens
- **Email Validation**: Don't reveal if email exists in system
- **Password Strength**: Enforce strong password requirements

## API Endpoints

### 1. Password Reset Request

**Endpoint**: `POST /api/auth/password-reset-request/`

**Description**: Initiates the password reset process by sending an email with reset instructions.

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Response** (200 OK):
```json
{
  "message": "If an account with this email exists, you will receive reset instructions."
}
```

**Security Notes**:
- Always return success message regardless of email existence
- Rate limit: 3 requests per email per hour
- Rate limit: 10 requests per IP per hour
- Log all attempts for security monitoring

**Backend Implementation**:
```python
# Example Django implementation
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.core.cache import cache
import hashlib
import time

def password_reset_request(request):
    email = request.data.get('email')
    
    # Rate limiting
    cache_key = f"reset_request_{email}"
    if cache.get(cache_key):
        return Response({"message": "If an account with this email exists, you will receive reset instructions."})
    
    # Check if user exists (but don't reveal)
    try:
        user = User.objects.get(email=email)
        
        # Generate secure token
        token = get_random_string(32)
        uid = str(user.id)
        
        # Store token in cache with expiration (1 hour)
        cache.set(f"reset_token_{uid}_{token}", True, 3600)
        
        # Send email
        reset_url = f"{settings.FRONTEND_URL}/password-reset-confirm?token={token}&uid={uid}"
        send_mail(
            'Password Reset Request',
            f'Click the link to reset your password: {reset_url}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        
    except User.DoesNotExist:
        pass  # Don't reveal if user exists
    
    # Set rate limit
    cache.set(cache_key, True, 3600)
    
    return Response({"message": "If an account with this email exists, you will receive reset instructions."})
```

### 2. Password Reset Validation

**Endpoint**: `POST /api/auth/password-reset-validate/`

**Description**: Validates if a password reset token is valid and not expired.

**Request Body**:
```json
{
  "token": "abc123...",
  "uid": "123"
}
```

**Response** (200 OK - Valid):
```json
{
  "valid": true,
  "message": "Token is valid"
}
```

**Response** (400 Bad Request - Invalid):
```json
{
  "valid": false,
  "message": "Invalid or expired token"
}
```

**Backend Implementation**:
```python
def password_reset_validate(request):
    token = request.data.get('token')
    uid = request.data.get('uid')
    
    # Check if token exists and is valid
    cache_key = f"reset_token_{uid}_{token}"
    if cache.get(cache_key):
        return Response({"valid": True, "message": "Token is valid"})
    else:
        return Response({"valid": False, "message": "Invalid or expired token"}, status=400)
```

### 3. Password Reset Confirmation

**Endpoint**: `POST /api/auth/password-reset-confirm/`

**Description**: Completes the password reset process with the new password.

**Request Body**:
```json
{
  "token": "abc123...",
  "uid": "123",
  "password": "NewSecurePassword123!",
  "confirm_password": "NewSecurePassword123!"
}
```

**Response** (200 OK):
```json
{
  "message": "Password has been reset successfully"
}
```

**Response** (400 Bad Request):
```json
{
  "message": "Invalid token, expired token, or passwords do not match"
}
```

**Backend Implementation**:
```python
def password_reset_confirm(request):
    token = request.data.get('token')
    uid = request.data.get('uid')
    password = request.data.get('password')
    confirm_password = request.data.get('confirm_password')
    
    # Validate token
    cache_key = f"reset_token_{uid}_{token}"
    if not cache.get(cache_key):
        return Response({"message": "Invalid or expired token"}, status=400)
    
    # Validate passwords match
    if password != confirm_password:
        return Response({"message": "Passwords do not match"}, status=400)
    
    # Validate password strength
    if not is_strong_password(password):
        return Response({"message": "Password does not meet strength requirements"}, status=400)
    
    try:
        # Get user and update password
        user = User.objects.get(id=uid)
        user.set_password(password)
        user.save()
        
        # Invalidate token (single use)
        cache.delete(cache_key)
        
        # Optional: Invalidate all user sessions
        user.auth_tokens.all().delete()
        
        return Response({"message": "Password has been reset successfully"})
        
    except User.DoesNotExist:
        return Response({"message": "Invalid user"}, status=400)

def is_strong_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.islower() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    return True
```

## Email Template

Create a professional email template for password reset:

```html
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
        
        <p>Hello,</p>
        
        <p>We received a request to reset your password for your Traible account. If you made this request, click the button below to reset your password:</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{{reset_url}}" 
               style="background-color: #88A0C2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                Reset Password
            </a>
        </div>
        
        <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
        <p style="word-break: break-all; color: #88A0C2;">{{reset_url}}</p>
        
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
```

## Security Considerations

### Rate Limiting
- Implement rate limiting at the API gateway level
- Use Redis or similar for distributed rate limiting
- Monitor for suspicious patterns

### Token Security
- Use cryptographically secure random token generation
- Store tokens in secure cache with expiration
- Implement single-use tokens
- Consider using JWT with short expiration for additional security

### Monitoring
- Log all password reset attempts
- Monitor for brute force attacks
- Set up alerts for unusual patterns
- Track failed attempts per IP/email

### Additional Security Features
- Consider implementing CAPTCHA for repeated failed attempts
- Add IP whitelisting for admin accounts
- Implement account lockout after multiple failed attempts
- Consider two-factor authentication for password resets

## Testing

### Test Cases
1. **Valid Reset Request**: User with valid email receives reset email
2. **Invalid Email**: Non-existent email returns success (security)
3. **Rate Limiting**: Multiple requests are rate limited
4. **Token Validation**: Valid tokens are accepted, invalid tokens rejected
5. **Token Expiration**: Expired tokens are rejected
6. **Single Use**: Used tokens cannot be reused
7. **Password Strength**: Weak passwords are rejected
8. **Password Mismatch**: Non-matching passwords are rejected

### Security Testing
- Test rate limiting boundaries
- Test token manipulation attempts
- Test concurrent reset requests
- Test expired token handling
- Test invalid user ID handling

## Implementation Checklist

- [ ] Create password reset request endpoint
- [ ] Create password reset validation endpoint  
- [ ] Create password reset confirmation endpoint
- [ ] Implement rate limiting
- [ ] Set up email service
- [ ] Create email templates
- [ ] Add password strength validation
- [ ] Implement token generation and storage
- [ ] Add logging and monitoring
- [ ] Write comprehensive tests
- [ ] Set up security alerts
- [ ] Document API endpoints
- [ ] Deploy and test in staging
- [ ] Monitor production usage
