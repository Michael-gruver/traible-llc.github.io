/**
 * Password validation utilities for secure password requirements
 */

export interface PasswordValidationResult {
  isValid: boolean;
  errors: string[];
  strength: PasswordStrength;
  score: number;
}

export enum PasswordStrength {
  WEAK = 'weak',
  MEDIUM = 'medium',
  STRONG = 'strong',
  VERY_STRONG = 'very_strong',
}

export interface PasswordRequirements {
  minLength: number;
  requireUppercase: boolean;
  requireLowercase: boolean;
  requireNumbers: boolean;
  requireSpecialChars: boolean;
  maxLength?: number;
  forbiddenPatterns?: RegExp[];
}

const DEFAULT_REQUIREMENTS: PasswordRequirements = {
  minLength: 8,
  requireUppercase: true,
  requireLowercase: true,
  requireNumbers: true,
  requireSpecialChars: false,
  maxLength: 128,
  forbiddenPatterns: [
    /(.)\1{2,}/, // No more than 2 consecutive identical characters
    /123|234|345|456|567|678|789|890/, // No sequential numbers
    /abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz/, // No sequential letters
  ],
};

/**
 * Validates a password against security requirements
 */
export function validatePassword(
  password: string,
  requirements: PasswordRequirements = DEFAULT_REQUIREMENTS
): PasswordValidationResult {
  const errors: string[] = [];
  let score = 0;

  // Length validation
  if (password.length < requirements.minLength) {
    errors.push(`Password must be at least ${requirements.minLength} characters long`);
  } else {
    score += 1;
  }

  if (requirements.maxLength && password.length > requirements.maxLength) {
    errors.push(`Password must be no more than ${requirements.maxLength} characters long`);
  }

  // Character type validation
  if (requirements.requireUppercase && !/[A-Z]/.test(password)) {
    errors.push('Password must contain at least one uppercase letter');
  } else if (requirements.requireUppercase) {
    score += 1;
  }

  if (requirements.requireLowercase && !/[a-z]/.test(password)) {
    errors.push('Password must contain at least one lowercase letter');
  } else if (requirements.requireLowercase) {
    score += 1;
  }

  if (requirements.requireNumbers && !/\d/.test(password)) {
    errors.push('Password must contain at least one number');
  } else if (requirements.requireNumbers) {
    score += 1;
  }

  if (requirements.requireSpecialChars && !/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
    errors.push('Password must contain at least one special character');
  } else if (requirements.requireSpecialChars) {
    score += 1;
  }

  // Forbidden patterns validation
  if (requirements.forbiddenPatterns) {
    for (const pattern of requirements.forbiddenPatterns) {
      if (pattern.test(password)) {
        errors.push('Password contains forbidden patterns (sequential or repeated characters)');
        break;
      }
    }
  }

  // Calculate strength
  const strength = calculatePasswordStrength(password, score);
  
  // Additional score based on length and complexity
  if (password.length >= 12) score += 1;
  if (password.length >= 16) score += 1;
  if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) score += 1;

  return {
    isValid: errors.length === 0,
    errors,
    strength,
    score: Math.min(score, 10), // Cap at 10
  };
}

/**
 * Calculates password strength based on various factors
 */
function calculatePasswordStrength(password: string, baseScore: number): PasswordStrength {
  let strengthScore = baseScore;

  // Length bonus
  if (password.length >= 12) strengthScore += 1;
  if (password.length >= 16) strengthScore += 1;

  // Character variety bonus
  const hasUppercase = /[A-Z]/.test(password);
  const hasLowercase = /[a-z]/.test(password);
  const hasNumbers = /\d/.test(password);
  const hasSpecialChars = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password);

  const charTypes = [hasUppercase, hasLowercase, hasNumbers, hasSpecialChars].filter(Boolean).length;
  strengthScore += charTypes - 1; // Bonus for multiple character types

  // Entropy calculation (simplified)
  const entropy = calculateEntropy(password);
  strengthScore += Math.floor(entropy / 10);

  if (strengthScore <= 2) return PasswordStrength.WEAK;
  if (strengthScore <= 4) return PasswordStrength.MEDIUM;
  if (strengthScore <= 6) return PasswordStrength.STRONG;
  return PasswordStrength.VERY_STRONG;
}

/**
 * Calculates password entropy (simplified version)
 */
function calculateEntropy(password: string): number {
  const charSet = new Set(password);
  const charsetSize = charSet.size;
  return Math.log2(Math.pow(charsetSize, password.length));
}

/**
 * Generates a secure random password
 */
export function generateSecurePassword(length: number = 16): string {
  const uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  const lowercase = 'abcdefghijklmnopqrstuvwxyz';
  const numbers = '0123456789';
  const specialChars = '!@#$%^&*()_+-=[]{}|;:,.<>?';

  const allChars = uppercase + lowercase + numbers + specialChars;
  let password = '';

  // Ensure at least one character from each type
  password += uppercase[Math.floor(Math.random() * uppercase.length)];
  password += lowercase[Math.floor(Math.random() * lowercase.length)];
  password += numbers[Math.floor(Math.random() * numbers.length)];
  password += specialChars[Math.floor(Math.random() * specialChars.length)];

  // Fill the rest randomly
  for (let i = 4; i < length; i++) {
    password += allChars[Math.floor(Math.random() * allChars.length)];
  }

  // Shuffle the password
  return password.split('').sort(() => Math.random() - 0.5).join('');
}

/**
 * Checks if password is commonly used (basic check)
 */
export function isCommonPassword(password: string): boolean {
  const commonPasswords = [
    'password', '123456', '123456789', 'qwerty', 'abc123',
    'password123', 'admin', 'letmein', 'welcome', 'monkey',
    '1234567890', 'password1', 'qwerty123', 'dragon', 'master',
    'hello', 'freedom', 'whatever', 'qazwsx', 'trustno1',
  ];

  return commonPasswords.includes(password.toLowerCase());
}

/**
 * Gets password strength color for UI
 */
export function getPasswordStrengthColor(strength: PasswordStrength): string {
  switch (strength) {
    case PasswordStrength.WEAK:
      return 'text-red-500';
    case PasswordStrength.MEDIUM:
      return 'text-yellow-500';
    case PasswordStrength.STRONG:
      return 'text-blue-500';
    case PasswordStrength.VERY_STRONG:
      return 'text-green-500';
    default:
      return 'text-gray-500';
  }
}

/**
 * Gets password strength background color for UI
 */
export function getPasswordStrengthBgColor(strength: PasswordStrength): string {
  switch (strength) {
    case PasswordStrength.WEAK:
      return 'bg-red-500';
    case PasswordStrength.MEDIUM:
      return 'bg-yellow-500';
    case PasswordStrength.STRONG:
      return 'bg-blue-500';
    case PasswordStrength.VERY_STRONG:
      return 'bg-green-500';
    default:
      return 'bg-gray-500';
  }
}

/**
 * Gets password strength text for UI
 */
export function getPasswordStrengthText(strength: PasswordStrength): string {
  switch (strength) {
    case PasswordStrength.WEAK:
      return 'Weak';
    case PasswordStrength.MEDIUM:
      return 'Medium';
    case PasswordStrength.STRONG:
      return 'Strong';
    case PasswordStrength.VERY_STRONG:
      return 'Very Strong';
    default:
      return 'Unknown';
  }
}
