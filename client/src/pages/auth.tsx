import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AuthForms } from "@/components/auth/auth-forms";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Auth() {
  const navigate = useNavigate();
  const [forgotPassword, setForgotPassword] = useState(false);
  useEffect(() => {
    if (localStorage.getItem("token"))
      navigate("/chat");
  }, [localStorage.getItem("token")])
  return (
    <div className="min-h-screen flex items-center justify-center bg-background text-foreground">
      <div className="container px-6 grid gap-12 md:grid-cols-2 items-center">
        {/* Left Side - Text Section */}
        <div className="max-w-lg">
          <h1 className="text-4xl font-bold leading-snug">
            Welcome to <span className="text-primary">Traible AI-Chatbot</span>
          </h1>
          <p className="text-lg mt-4 text-muted-foreground leading-relaxed">
            Your AI-powered assistant. Get instant answers to your questions and intelligent analysis of your documents.
          </p>
        </div>

        {/* Right Side - Auth Card */}
        <div className="md:max-w-md w-full">
          <Card className="border bg-card text-card-foreground shadow-md">
            <CardHeader>
              <CardTitle className="text-2xl font-semibold text-center">{forgotPassword ? "Reset password" : "Get Started"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <AuthForms setForgotPassword={setForgotPassword} forgotPassword={forgotPassword} />
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
