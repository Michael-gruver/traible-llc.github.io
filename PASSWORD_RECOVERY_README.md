# Password Recovery System

A comprehensive and secure password recovery system for the Traible application.

## Features

### 🔐 **Security Features**
- **Rate Limiting**: Prevents brute force attacks
- **Token Expiration**: Reset tokens expire after 1 hour
- **Single Use Tokens**: Tokens are invalidated after use
- **Secure Token Generation**: Cryptographically secure random tokens
- **Email Privacy**: Doesn't reveal if email exists in system
- **Password Strength Validation**: Enforces strong password requirements

### 🎨 **User Experience**
- **Modern UI**: Clean, responsive design with animations
- **Password Strength Indicator**: Real-time password strength feedback
- **Password Generator**: Built-in secure password generator
- **Progressive Enhancement**: Works without JavaScript for basic functionality
- **Accessibility**: Full keyboard navigation and screen reader support

### 🛠 **Developer Experience**
- **TypeScript**: Full type safety
- **Reusable Components**: Modular, composable components
- **Custom Hooks**: Clean separation of logic and UI
- **Comprehensive Testing**: Unit and integration tests
- **Documentation**: Detailed API and implementation docs

## Components

### Pages
- **`/password-reset-request`** - Request password reset
- **`/password-reset-confirm`** - Confirm password reset with token

### Components
- **`PasswordStrengthInput`** - Enhanced password input with strength indicator
- **`PasswordRecovery`** - Main recovery flow component

### Hooks
- **`usePasswordRecovery`** - Password recovery logic
- **`usePasswordValidation`** - Password validation utilities

### Utilities
- **`password-utils.ts`** - Password validation and generation utilities

## Usage

### Frontend Integration

The password recovery system is already integrated into your auth flow:

1. **Login Page**: "Forgot Password?" link redirects to `/password-reset-request`
2. **Reset Request**: User enters email, receives reset link
3. **Reset Confirmation**: User clicks link, sets new password
4. **Success**: User redirected to login with new password

### Backend API Requirements

You need to implement these endpoints:

```typescript
// 1. Request password reset
POST /api/auth/password-reset-request/
{
  "email": "user@example.com"
}

// 2. Validate reset token
POST /api/auth/password-reset-validate/
{
  "token": "abc123...",
  "uid": "123"
}

// 3. Confirm password reset
POST /api/auth/password-reset-confirm/
{
  "token": "abc123...",
  "uid": "123",
  "password": "NewSecurePassword123!",
  "confirm_password": "NewSecurePassword123!"
}
```

See `PASSWORD_RECOVERY_API.md` for detailed backend implementation.

## Password Requirements

### Default Requirements
- **Minimum Length**: 8 characters
- **Uppercase Letters**: At least 1
- **Lowercase Letters**: At least 1
- **Numbers**: At least 1
- **Special Characters**: Optional (configurable)
- **Maximum Length**: 128 characters

### Forbidden Patterns
- More than 2 consecutive identical characters
- Sequential numbers (123, 234, etc.)
- Sequential letters (abc, bcd, etc.)

### Strength Levels
- **Weak**: Basic requirements not met
- **Medium**: Basic requirements met
- **Strong**: Multiple character types, good length
- **Very Strong**: Excellent entropy and complexity

## Security Considerations

### Rate Limiting
- **Per Email**: 3 requests per hour
- **Per IP**: 10 requests per hour
- **Global**: 100 requests per hour

### Token Security
- **Generation**: Cryptographically secure random strings
- **Storage**: Secure cache with expiration
- **Transmission**: HTTPS only
- **Validation**: Server-side validation required

### Monitoring
- **Logging**: All attempts logged
- **Alerts**: Suspicious patterns flagged
- **Metrics**: Success/failure rates tracked

## Customization

### Password Requirements
```typescript
import { validatePassword } from '@/lib/password-utils';

const customRequirements = {
  minLength: 12,
  requireUppercase: true,
  requireLowercase: true,
  requireNumbers: true,
  requireSpecialChars: true,
  maxLength: 64,
};

const validation = validatePassword(password, customRequirements);
```

### UI Customization
```typescript
<PasswordStrengthInput
  value={password}
  onChange={setPassword}
  showStrengthIndicator={true}
  showGenerateButton={true}
  className="custom-class"
/>
```

### Email Templates
Customize email templates in your backend implementation. See `PASSWORD_RECOVERY_API.md` for examples.

## Testing

### Manual Testing
1. **Request Reset**: Enter valid email, check for success message
2. **Invalid Email**: Enter non-existent email, verify same response
3. **Rate Limiting**: Make multiple requests, verify rate limiting
4. **Token Validation**: Use valid/invalid tokens
5. **Password Strength**: Test various password strengths
6. **Token Expiration**: Wait for token to expire, verify rejection

### Automated Testing
```bash
# Run password recovery tests
npm run test -- --grep "password recovery"

# Run password validation tests
npm run test -- --grep "password validation"
```

## Deployment

### Environment Variables
```bash
# Frontend
VITE_API_URL=https://api.traible.com

# Backend (for reference)
DATABASE_URL=postgresql://...
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
FRONTEND_URL=https://traible.com
```

### Production Checklist
- [ ] HTTPS enabled
- [ ] Rate limiting configured
- [ ] Email service configured
- [ ] Token storage secured
- [ ] Monitoring enabled
- [ ] Error handling tested
- [ ] Performance tested
- [ ] Security audit completed

## Troubleshooting

### Common Issues

**"Invalid or expired token"**
- Token may have expired (1 hour limit)
- Token may have been used already
- Check URL parameters are correct

**"Rate limit exceeded"**
- Wait before making another request
- Check if multiple users are using same IP

**"Email not received"**
- Check spam folder
- Verify email address is correct
- Check email service configuration

**"Password doesn't meet requirements"**
- Use password strength indicator
- Try password generator
- Check requirements documentation

### Debug Mode
Enable debug logging in development:
```typescript
// In your backend
DEBUG_PASSWORD_RECOVERY=true
```

## Support

For issues or questions:
1. Check this documentation
2. Review API specification
3. Check error logs
4. Contact development team

## Changelog

### v1.0.0
- Initial implementation
- Basic password recovery flow
- Security features
- UI components
- Documentation

## License

This password recovery system is part of the Traible application and follows the same license terms.
