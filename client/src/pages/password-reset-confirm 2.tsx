import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { motion } from 'framer-motion';
import { CheckCircle, AlertCircle } from 'lucide-react';
import { PasswordStrengthInput } from '@/components/common/PasswordStrengthInput';
import axios from 'axios';

// Schema for password reset confirmation
const resetConfirmSchema = z
  .object({
    password: z
      .string()
      .min(8, 'Password must be at least 8 characters')
      .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, 'Password must contain at least one uppercase letter, one lowercase letter, and one number'),
    confirmPassword: z.string().min(8, 'Please confirm your password'),
  })
  .refine(data => data.password === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  });

type ResetConfirmForm = z.infer<typeof resetConfirmSchema>;

export default function PasswordResetConfirm() {
  const [loading, setLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [isValidToken, setIsValidToken] = useState<boolean | null>(null);
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const url = import.meta.env.VITE_API_URL;

  const token = searchParams.get('token');
  const uid = searchParams.get('uid');

  const form = useForm<ResetConfirmForm>({
    resolver: zodResolver(resetConfirmSchema),
    defaultValues: {
      password: '',
      confirmPassword: '',
    },
  });

  // Validate token on component mount
  useEffect(() => {
    const validateToken = async () => {
      if (!token || !uid) {
        setIsValidToken(false);
        return;
      }

      try {
        const response = await axios.post(`${url}/api/auth/password-reset-validate/`, {
          token,
          uid,
        });

        if (response.status === 200) {
          setIsValidToken(true);
        } else {
          setIsValidToken(false);
        }
      } catch (error) {
        console.error('Token validation error:', error);
        setIsValidToken(false);
      }
    };

    validateToken();
  }, [token, uid, url]);

  const onSubmit = async (data: ResetConfirmForm) => {
    if (!token || !uid) {
      toast({
        title: 'Invalid Reset Link',
        description: 'The password reset link is invalid or expired.',
        variant: 'destructive',
      });
      return;
    }

    try {
      setLoading(true);
      
      const response = await axios.post(`${url}/api/auth/password-reset-confirm/`, {
        token,
        uid,
        password: data.password,
        confirm_password: data.confirmPassword,
      });

      if (response.status === 200) {
        setIsSuccess(true);
        toast({
          title: 'Password Reset Successful',
          description: 'Your password has been updated successfully.',
        });
      }
    } catch (error: any) {
      console.error('Password reset confirmation error:', error);
      
      const errorMessage = error.response?.data?.message || 'Failed to reset password. Please try again.';
      toast({
        title: 'Reset Failed',
        description: errorMessage,
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  // Loading state while validating token
  if (isValidToken === null) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background p-4">
        <div className="text-center">
          <LoadingSpinner />
          <p className="mt-4 text-muted-foreground">Validating reset link...</p>
        </div>
      </div>
    );
  }

  // Invalid token state
  if (isValidToken === false) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background p-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-md"
        >
          <Card>
            <CardHeader className="text-center">
              <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-red-100 dark:bg-red-900">
                <AlertCircle className="h-6 w-6 text-red-600 dark:text-red-400" />
              </div>
              <CardTitle className="text-2xl">Invalid Reset Link</CardTitle>
              <CardDescription>
                This password reset link is invalid or has expired.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="text-center text-sm text-muted-foreground">
                <p>Please request a new password reset link.</p>
              </div>
              <div className="pt-4 space-y-2">
                <Button
                  onClick={() => navigate('/password-reset-request')}
                  className="w-full"
                >
                  Request New Reset Link
                </Button>
                <Button
                  variant="outline"
                  onClick={() => navigate('/auth')}
                  className="w-full"
                >
                  Back to Login
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    );
  }

  // Success state
  if (isSuccess) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background p-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-md"
        >
          <Card>
            <CardHeader className="text-center">
              <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-green-100 dark:bg-green-900">
                <CheckCircle className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
              <CardTitle className="text-2xl">Password Reset Complete</CardTitle>
              <CardDescription>
                Your password has been successfully updated.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="text-center text-sm text-muted-foreground">
                <p>You can now log in with your new password.</p>
              </div>
              <div className="pt-4">
                <Button
                  onClick={() => navigate('/auth')}
                  className="w-full"
                >
                  Continue to Login
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    );
  }

  // Main form
  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        <Card>
          <CardHeader className="text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
              <CheckCircle className="h-6 w-6 text-primary" />
            </div>
            <CardTitle className="text-2xl">Set New Password</CardTitle>
            <CardDescription>
              Enter your new password below.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                <FormField
                  control={form.control}
                  name="password"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>New Password</FormLabel>
                      <FormControl>
                        <PasswordStrengthInput
                          value={field.value}
                          onChange={field.onChange}
                          placeholder="Enter your new password"
                          disabled={loading}
                          showStrengthIndicator={true}
                          showGenerateButton={true}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="confirmPassword"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Confirm New Password</FormLabel>
                      <FormControl>
                        <PasswordStrengthInput
                          value={field.value}
                          onChange={field.onChange}
                          placeholder="Confirm your new password"
                          disabled={loading}
                          showStrengthIndicator={false}
                          showGenerateButton={false}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <Button type="submit" className="w-full" disabled={loading}>
                  {loading ? (
                    <>
                      <LoadingSpinner />
                      Updating Password...
                    </>
                  ) : (
                    'Update Password'
                  )}
                </Button>
              </form>
            </Form>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
