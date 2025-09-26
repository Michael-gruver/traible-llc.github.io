import { useState, useMemo } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Eye, EyeOff, RefreshCw } from 'lucide-react';
import {
  validatePassword,
  generateSecurePassword,
  getPasswordStrengthColor,
  getPasswordStrengthBgColor,
  getPasswordStrengthText,
  PasswordStrength,
} from '@/lib/password-utils';

interface PasswordStrengthInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  showStrengthIndicator?: boolean;
  showGenerateButton?: boolean;
  className?: string;
}

export function PasswordStrengthInput({
  value,
  onChange,
  placeholder = 'Enter password',
  disabled = false,
  showStrengthIndicator = true,
  showGenerateButton = true,
  className = '',
}: PasswordStrengthInputProps) {
  const [showPassword, setShowPassword] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  const validation = useMemo(() => {
    if (!value) return null;
    return validatePassword(value);
  }, [value]);

  const handleGeneratePassword = async () => {
    setIsGenerating(true);
    // Small delay for better UX
    await new Promise(resolve => setTimeout(resolve, 500));
    const newPassword = generateSecurePassword(16);
    onChange(newPassword);
    setIsGenerating(false);
  };

  const getStrengthBarWidth = (strength: PasswordStrength): string => {
    switch (strength) {
      case PasswordStrength.WEAK:
        return '25%';
      case PasswordStrength.MEDIUM:
        return '50%';
      case PasswordStrength.STRONG:
        return '75%';
      case PasswordStrength.VERY_STRONG:
        return '100%';
      default:
        return '0%';
    }
  };

  return (
    <div className={`space-y-2 ${className}`}>
      <div className="relative">
        <Input
          type={showPassword ? 'text' : 'password'}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          disabled={disabled}
          className="pr-20"
        />
        <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center space-x-1">
          {showGenerateButton && (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={handleGeneratePassword}
              disabled={disabled || isGenerating}
              className="h-6 w-6 p-0"
              title="Generate secure password"
            >
              <RefreshCw className={`h-3 w-3 ${isGenerating ? 'animate-spin' : ''}`} />
            </Button>
          )}
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => setShowPassword(!showPassword)}
            disabled={disabled}
            className="h-6 w-6 p-0"
            title={showPassword ? 'Hide password' : 'Show password'}
          >
            {showPassword ? (
              <EyeOff className="h-3 w-3" />
            ) : (
              <Eye className="h-3 w-3" />
            )}
          </Button>
        </div>
      </div>

      {showStrengthIndicator && value && validation && (
        <div className="space-y-2">
          {/* Strength Bar */}
          <div className="flex items-center space-x-2">
            <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all duration-300 ${getPasswordStrengthBgColor(validation.strength)}`}
                style={{ width: getStrengthBarWidth(validation.strength) }}
              />
            </div>
            <span className={`text-xs font-medium ${getPasswordStrengthColor(validation.strength)}`}>
              {getPasswordStrengthText(validation.strength)}
            </span>
          </div>

          {/* Validation Messages */}
          {validation.errors.length > 0 && (
            <div className="space-y-1">
              {validation.errors.map((error, index) => (
                <p key={index} className="text-xs text-red-500">
                  • {error}
                </p>
              ))}
            </div>
          )}

          {/* Success Messages */}
          {validation.isValid && (
            <p className="text-xs text-green-500">
              ✓ Password meets all requirements
            </p>
          )}
        </div>
      )}
    </div>
  );
}
