import { useState } from 'react';
import { useToast } from './use-toast';
import axios from 'axios';

interface PasswordRecoveryState {
  loading: boolean;
  error: string | null;
  success: boolean;
}

interface PasswordRecoveryActions {
  requestPasswordReset: (email: string) => Promise<void>;
  validateResetToken: (token: string, uid: string) => Promise<boolean>;
  confirmPasswordReset: (token: string, uid: string, password: string, confirmPassword: string) => Promise<void>;
  resetState: () => void;
}

export function usePasswordRecovery(): PasswordRecoveryState & PasswordRecoveryActions {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const { toast } = useToast();
  const url = import.meta.env.VITE_API_URL;

  const requestPasswordReset = async (email: string): Promise<void> => {
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const response = await axios.post(`${url}/api/auth/password-reset-request/`, {
        email,
      });

      if (response.status === 200) {
        setSuccess(true);
        toast({
          title: 'Reset Link Sent',
          description: 'Check your email for password reset instructions.',
        });
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to send reset link. Please try again.';
      setError(errorMessage);
      
      // Don't reveal if email exists for security
      toast({
        title: 'Reset Link Sent',
        description: 'If an account with this email exists, you will receive reset instructions.',
        variant: 'default',
      });
    } finally {
      setLoading(false);
    }
  };

  const validateResetToken = async (token: string, uid: string): Promise<boolean> => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${url}/api/auth/password-reset-validate/`, {
        token,
        uid,
      });

      if (response.status === 200 && response.data.valid) {
        return true;
      } else {
        setError('Invalid or expired reset token');
        return false;
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Invalid or expired reset token';
      setError(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const confirmPasswordReset = async (
    token: string,
    uid: string,
    password: string,
    confirmPassword: string
  ): Promise<void> => {
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const response = await axios.post(`${url}/api/auth/password-reset-confirm/`, {
        token,
        uid,
        password,
        confirm_password: confirmPassword,
      });

      if (response.status === 200) {
        setSuccess(true);
        toast({
          title: 'Password Reset Successful',
          description: 'Your password has been updated successfully.',
        });
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to reset password. Please try again.';
      setError(errorMessage);
      toast({
        title: 'Reset Failed',
        description: errorMessage,
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const resetState = (): void => {
    setLoading(false);
    setError(null);
    setSuccess(false);
  };

  return {
    loading,
    error,
    success,
    requestPasswordReset,
    validateResetToken,
    confirmPasswordReset,
    resetState,
  };
}
