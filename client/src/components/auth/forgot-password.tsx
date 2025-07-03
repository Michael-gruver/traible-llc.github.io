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
import { useToast } from "@/hooks/use-toast";
import { useSetRecoilState } from "recoil";
import { isAuthenticatedState } from "@/store/auth";
import { useLocation } from "wouter";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { motion } from "framer-motion";
import { PasswordInput } from "../common/PasswordInput";
import { useNavigate, Link } from "react-router-dom";

const baseSchema = z.object({
    email: z.string().email(),
    password: z.string().min(6),
    confirm_password: z.string().min(6),
    username: z.string().min(3),
});

export function ForgotPassword({ setForgotPassword }) {
    const loginSchema = baseSchema.omit({
        username: true,
        confirm_password: true,
        password: true,
    });

    const loginForm = useForm<z.infer<typeof loginSchema>>({
        resolver: zodResolver(loginSchema),
    });

    const [loading, setLoading] = useState(false);
    const [isSuccess, setIsSuccess] = useState(false);
    const url = import.meta.env.VITE_API_URL;
    const setIsAuthenticated = useSetRecoilState(isAuthenticatedState);
    const { toast } = useToast();



    async function onPasswordReset(values: z.infer<typeof loginSchema>) {
        try {
            setLoading(true);
            const response = await axios.post(`${url}/api/auth/forgot-password/`, {
                email: values.email
            });
            console.log("~s onPasswordReset ~ response:", response)
            localStorage.setItem("token", response?.data?.access);
            setLoading(false);
            setIsAuthenticated(true);
            setIsSuccess(true)
            toast({ title: "Success", description: "Password reset link sent successfully" });
            navigate("/auth");
        } catch (error: any) {
            setLoading(false);
            toast({ title: "Error", description: error.response?.data?.message || "Login failed" });
        }
    }
    return (
        <>
            <Form {...loginForm}>
                <form onSubmit={loginForm.handleSubmit(onPasswordReset)} >
                    <FormField
                        control={loginForm.control}
                        name="email"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Email</FormLabel>
                                <FormControl>
                                    <Input placeholder="Enter email" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    {isSuccess ? <p>Check your email for a password reset link!</p> : <Button type="submit" disabled={loading} className="mt-4">{loading ? <LoadingSpinner /> : "Continue"}</Button>}
                </form>
            </Form>
            <Button
                className="bg-transparent text-white px-4 py-2 w-27 max-w-xs shadow-none border-none hover:text-gray-300 mt-2 mb-2"
                onClick={() => { setForgotPassword(false) }}>Back</Button>
        </>
    );
}