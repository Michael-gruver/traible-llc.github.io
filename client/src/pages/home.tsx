import { Link } from "wouter";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { FileText, MessageSquare, Shield } from "lucide-react";
import { useNavigate } from "react-router-dom";
import Triable from "../../assets/Traible.png";
import { useEffect } from "react";
export default function Home() {
  const navigate = useNavigate();

  useEffect(() => {
    if (localStorage.getItem("token"))
     navigate("/chat");
  }, [localStorage.getItem("token")])
  
  return (
    <div className="container mx-auto px-4 py-16">
      <div className="text-center mb-16">
        {/* Logo Image */}
        <div className="flex justify-center mb-2">
          <img src={Triable} alt="Traible Logo" className="h-16 md:h-20" />
        </div>

        {/* Styled Subheading */}
        <h2 className="text-3xl  mb-6 font-bold bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent">
          Know Your Tribe
        </h2>

        {/* Description */}
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          Unlock Your Organization's Expert Knowledge.<br />
          Transform undocumented expertise into a powerful, accessible asset for your entire team.
        </p>

        {/* Call to Action Button */}
        <Button onClick={() => navigate("/auth")} size="lg" className="mt-10 px-6 py-3 text-lg font-medium shadow-lg">
          Get Started
        </Button>
      </div>



      <div className="grid md:grid-cols-3 gap-8 mt-16">
        <Card>
          <CardContent className="pt-6">
            <FileText className="w-12 h-12 text-primary mb-4" />
            <h3 className="text-lg font-semibold mb-2">Document Processing</h3>
            <p className="text-muted-foreground">
              Upload documents and let Traible extract key insights tailored to your organization.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <MessageSquare className="w-12 h-12 text-primary mb-4" />
            <h3 className="text-lg font-semibold mb-2">Intelligent Chat</h3>
            <p className="text-muted-foreground">
              Ask questions and get instant, expert answers based on your company's knowledge.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <Shield className="w-12 h-12 text-primary mb-4" />
            <h3 className="text-lg font-semibold mb-2">Secure & Private</h3>
            <p className="text-muted-foreground">
              Your data is encrypted and handled with the utmost security.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
