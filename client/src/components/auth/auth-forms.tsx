import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import axios from "axios";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { ForgotPassword } from "@/components/auth/forgot-password";
import { useToast } from "@/hooks/use-toast";
import { useSetRecoilState } from "recoil";
import { isAuthenticatedState } from "@/store/auth";
import { useLocation } from "wouter";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { motion } from "framer-motion";
import { PasswordInput } from "../common/PasswordInput";
import { useNavigate, Link } from "react-router-dom";

// Schema for validation
const authSchema = z.object({
  email: z.string(),
  password: z.string().min(6),
  confirm_password: z.string().min(6),
  username: z.string().min(3),
}).refine((data) => data.password === data.confirm_password, {
  message: "Passwords do not match",
  path: ["confirm_password"],
});
const baseSchema = z.object({
  email: z.string(),
  password: z.string().min(6),
  confirm_password: z.string().min(6),
  username: z.string().min(3),
});


export function AuthForms({ setForgotPassword, forgotPassword }) {
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();
  const url = import.meta.env.VITE_API_URL;
  console.log(url);
  const setIsAuthenticated = useSetRecoilState(isAuthenticatedState);
  const [location, setLocation] = useLocation();
  // const handleNavigate = () => {
  //   navigate("/chat"); // Navigates to /dashboard
  // };
  const navigate = useNavigate()
  const loginSchema = baseSchema.omit({ username: true, confirm_password: true });

  const loginForm = useForm<z.infer<typeof loginSchema>>({
    resolver: zodResolver(loginSchema),
  });
  const signupForm = useForm<z.infer<typeof authSchema>>({
    resolver: zodResolver(authSchema),
    defaultValues: {
      email: "",
      password: "",
      confirm_password: "",
      username: "",
    },
  });

  async function onLogin(values: z.infer<typeof loginSchema>) {
    try {
      setLoading(true);
      const response = await axios.post(`${url}/api/auth/login/`, {
        username_or_email: values.email,
        password: values.password,
      });
      console.log("🚀 ~ onLogin ~ response:", response)
      localStorage.setItem("token", response?.data?.access);
      setLoading(false);
      setIsAuthenticated(true);
      toast({ title: "Success", description: "Logged in successfully" });
      navigate("/chat");

    } catch (error: any) {
      setLoading(false);
      toast({ title: "Error", description: error.response?.data?.message || "Login failed" });
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
      localStorage.setItem("token", response?.data?.access);
      setIsAuthenticated(true);
      toast({ title: "Success", description: "Account created successfully." });
      navigate("/chat");
    } catch (error: any) {
      setLoading(false);
      toast({ title: "Error", description: error.response?.data?.error || "Signup failed" });
    }
  }

  return (
    <>
      {!forgotPassword ?
        <Tabs defaultValue="login" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="login">Login</TabsTrigger>
            <TabsTrigger value="signup">Sign Up</TabsTrigger>
          </TabsList>

          {/* Login Form */}
          <TabsContent value="login">
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
              <Form {...loginForm}>
                <form onSubmit={loginForm.handleSubmit(onLogin)} className="space-y-4">
                  <FormField
                    control={loginForm.control}
                    name="email"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Email or Username</FormLabel> {/* Updated label */}
                        <FormControl>
                          <Input placeholder="Enter email or username" {...field} />
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
                          <PasswordInput field={field} placeholder="Choose a password" />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <Button
                    type="button"
                    onClick={() => {
                      setForgotPassword(true)
                      console.log('forgot password value--->', forgotPassword)
                    }}
                    className="p-0 m-0 text-blue-600 hover:underline bg-transparent border-none shadow-none">
                    Forgot password?
                  </Button>
                  <Button type="submit" className="w-full" disabled={loading}>
                    {loading ? <LoadingSpinner /> : "Login"}
                  </Button>

                </form>
              </Form>
            </motion.div>
          </TabsContent>

          {/* Signup Form */}
          <TabsContent value="signup">
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
              <Form {...signupForm}>
                <form onSubmit={signupForm.handleSubmit(onSignup)} className="space-y-4">
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
                          <PasswordInput field={field} placeholder="Choose a password" />
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
                          <PasswordInput field={field} placeholder="Choose a password" />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <Button type="submit" className="w-full" disabled={loading}>
                    {loading ? <LoadingSpinner /> : "Create Account"}
                  </Button>
                </form>
              </Form>
            </motion.div>
          </TabsContent>
        </Tabs> : <ForgotPassword setForgotPassword={setForgotPassword} />
      }
    </>
  );
}
