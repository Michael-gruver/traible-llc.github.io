import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { ForgotPassword } from '@/components/auth/forgot-password';
import { useToast } from '@/hooks/use-toast';
import { useAuthStore } from '@/store/auth';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { motion } from 'framer-motion';
import { PasswordInput } from '../common/PasswordInput';
import { useNavigate, Link } from 'react-router-dom';
import { KeyRound, ArrowRight, Sparkles } from 'lucide-react';

// Schema for validation
const authSchema = z
  .object({
    email: z.string(),
    password: z.string().min(6),
    confirm_password: z.string().min(6),
    username: z.string().min(3),
  })
  .refine(data => data.password === data.confirm_password, {
    message: 'Passwords do not match',
    path: ['confirm_password'],
  });
const baseSchema = z.object({
  email: z.string(),
  password: z.string().min(6),
  confirm_password: z.string().min(6),
  username: z.string().min(3),
});

export function AuthForms({ setForgotPassword, forgotPassword }: { setForgotPassword: (value: boolean) => void; forgotPassword: boolean }) {
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();
  const url = import.meta.env.VITE_API_URL;
  console.log(url);
  const { setToken } = useAuthStore();
  // const handleNavigate = () => {
  //   navigate("/chat"); // Navigates to /dashboard
  // };
  const navigate = useNavigate();
  const loginSchema = baseSchema.omit({
    username: true,
    confirm_password: true,
  });

  const loginForm = useForm<z.infer<typeof loginSchema>>({
    resolver: zodResolver(loginSchema),
  });
  const signupForm = useForm<z.infer<typeof authSchema>>({
    resolver: zodResolver(authSchema),
    defaultValues: {
      email: '',
      password: '',
      confirm_password: '',
      username: '',
    },
  });

  async function onLogin(values: z.infer<typeof loginSchema>) {
    try {
      setLoading(true);
      const response = await axios.post(`${url}/api/auth/login/`, {
        username_or_email: values.email,
        password: values.password,
      });
      console.log('🚀 ~ onLogin ~ response:', response);
      setToken(response?.data?.access);
      setLoading(false);
      toast({ title: 'Success', description: 'Logged in successfully' });
      navigate('/chat');
    } catch (error: any) {
      setLoading(false);
      toast({
        title: 'Error',
        description: error.response?.data?.message || 'Login failed',
      });
    }
  }

  async function onSignup(values: z.infer<typeof authSchema>) {
    try {
      setLoading(true);
      const response = await axios.post(`${url}/api/auth/signup/`, {
        email: values.email,
        username: values.username,
        password: values.password,
        confirm_password: values.confirm_password,
      });

      setLoading(false);
      setToken(response?.data?.access);
      toast({ title: 'Success', description: 'Account created successfully.' });
      navigate('/chat');
    } catch (error: any) {
      setLoading(false);
      toast({
        title: 'Error',
        description: error.response?.data?.error || 'Signup failed',
      });
    }
  }

  return (
    <>
      {!forgotPassword ? (
        <Tabs defaultValue="login" className="w-full">
          <TabsList className="grid w-full grid-cols-2 bg-gray-800/80 p-1 rounded-xl border border-gray-700/50 backdrop-blur-sm">
            <TabsTrigger 
              value="login" 
              className="data-[state=active]:bg-gray-900/90 data-[state=active]:shadow-lg data-[state=active]:text-blue-400 data-[state=active]:border data-[state=active]:border-blue-500/30 font-medium transition-all duration-200 rounded-lg text-gray-300 hover:text-gray-100"
            >
              Sign In
            </TabsTrigger>
            <TabsTrigger 
              value="signup" 
              className="data-[state=active]:bg-gray-900/90 data-[state=active]:shadow-lg data-[state=active]:text-emerald-400 data-[state=active]:border data-[state=active]:border-emerald-500/30 font-medium transition-all duration-200 rounded-lg text-gray-300 hover:text-gray-100"
            >
              Sign Up
            </TabsTrigger>
          </TabsList>

          {/* Login Form */}
          <TabsContent value="login">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <Form {...loginForm}>
                <form
                  onSubmit={loginForm.handleSubmit(onLogin)}
                  className="space-y-4"
                >
                  <FormField
                    control={loginForm.control}
                    name="email"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Email or Username</FormLabel>{' '}
                        {/* Updated label */}
                        <FormControl>
                          <Input
                            placeholder="Enter email or username"
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={loginForm.control}
                    name="password"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Password</FormLabel>
                        <FormControl>
                          <PasswordInput
                            field={field}
                            placeholder="Choose a password"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <motion.div
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="w-full"
                  >
                    <Link to="/password-reset-request" className="block">
                      <Button
                        type="button"
                        variant="ghost"
                        className="w-full group relative overflow-hidden bg-gradient-to-r from-gray-800/60 to-gray-900/60 hover:from-gray-700/80 hover:to-gray-800/80 border border-gray-600/40 hover:border-gray-500/60 text-gray-300 hover:text-gray-100 transition-all duration-300 ease-out shadow-lg hover:shadow-xl backdrop-blur-sm"
                      >
                        <div className="flex items-center justify-center space-x-2 relative z-10">
                          <KeyRound className="h-4 w-4 transition-transform duration-300 group-hover:rotate-12" />
                          <span className="font-medium text-sm">Forgot your password?</span>
                          <ArrowRight className="h-3 w-3 transition-transform duration-300 group-hover:translate-x-1" />
                        </div>
                        <div className="absolute inset-0 bg-gradient-to-r from-blue-400/20 to-indigo-400/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                        <Sparkles className="absolute top-1 right-1 h-3 w-3 text-blue-400/80 opacity-0 group-hover:opacity-100 transition-all duration-300 group-hover:animate-pulse" />
                      </Button>
                    </Link>
                  </motion.div>
                  <motion.div
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="w-full"
                  >
                    <Button 
                      type="submit" 
                      className="w-full group relative overflow-hidden bg-gradient-to-r from-gray-800 to-gray-900 hover:from-gray-700 hover:to-gray-800 text-gray-100 shadow-lg hover:shadow-xl transition-all duration-300 ease-out border border-gray-600/50 hover:border-gray-500/70" 
                      disabled={loading}
                    >
                      <div className="flex items-center justify-center space-x-2 relative z-10">
                        {loading ? (
                          <LoadingSpinner />
                        ) : (
                          <>
                            <span className="font-semibold">Sign In</span>
                            <ArrowRight className="h-4 w-4 transition-transform duration-300 group-hover:translate-x-1" />
                          </>
                        )}
                      </div>
                      <div className="absolute inset-0 bg-gradient-to-r from-gray-400/10 to-gray-300/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                    </Button>
                  </motion.div>
                </form>
              </Form>
            </motion.div>
          </TabsContent>

          {/* Signup Form */}
          <TabsContent value="signup">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <Form {...signupForm}>
                <form
                  onSubmit={signupForm.handleSubmit(onSignup)}
                  className="space-y-4"
                >
                  <FormField
                    control={signupForm.control}
                    name="username"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Username</FormLabel>
                        <FormControl>
                          <Input placeholder="Choose a username" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={signupForm.control}
                    name="email"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Email</FormLabel>
                        <FormControl>
                          <Input placeholder="Enter your email" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={signupForm.control}
                    name="password"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Password</FormLabel>
                        <FormControl>
                          <PasswordInput
                            field={field}
                            placeholder="Choose a password"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={signupForm.control}
                    name="confirm_password"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Confirm Password</FormLabel>
                        <FormControl>
                          <PasswordInput
                            field={field}
                            placeholder="Choose a password"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <motion.div
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="w-full"
                  >
                    <Button 
                      type="submit" 
                      className="w-full group relative overflow-hidden bg-gradient-to-r from-gray-800 to-gray-900 hover:from-gray-700 hover:to-gray-800 text-gray-100 shadow-lg hover:shadow-xl transition-all duration-300 ease-out border border-gray-600/50 hover:border-gray-500/70" 
                      disabled={loading}
                    >
                      <div className="flex items-center justify-center space-x-2 relative z-10">
                        {loading ? (
                          <LoadingSpinner />
                        ) : (
                          <>
                            <span className="font-semibold">Create Account</span>
                            <ArrowRight className="h-4 w-4 transition-transform duration-300 group-hover:translate-x-1" />
                          </>
                        )}
                      </div>
                      <div className="absolute inset-0 bg-gradient-to-r from-gray-400/10 to-gray-300/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                    </Button>
                  </motion.div>
                </form>
              </Form>
            </motion.div>
          </TabsContent>
        </Tabs>
      ) : (
        <ForgotPassword setForgotPassword={setForgotPassword} />
      )}
    </>
  );
}
