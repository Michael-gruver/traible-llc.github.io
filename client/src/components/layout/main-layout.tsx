// import { Link } from "wouter";
// import { Button } from "@/components/ui/button";
// import { ModeToggle } from "@/components/ui/toggle-mode";
// import { useRecoilState, useRecoilValue } from "recoil";
// import { isAuthenticatedState } from "@/store/auth";
// import { LogOut, MessageSquare } from "lucide-react";
// import { navigate } from "wouter/use-browser-location";
// import { useNavigate } from "react-router-dom";
// import { selectedConversationIdState } from "@/store/chat";
// import logoIcon from "../../../assets/logo.jpg";

// export default function MainLayout({ children }: { children: React.ReactNode }) {
//   const [isAuthenticated, setIsAuthenticated] = useRecoilState(isAuthenticatedState);
//   const [selectedConversationId, setSelectedConversationId] = useRecoilState(selectedConversationIdState);
//   const url = import.meta.env.VITE_API_URL;
//   console.log(url);
//   const handleSelectConversation = async () => {
//     try {
//       const token = localStorage.getItem("token");
//       const response = await fetch(`${url}/api/conversations/initialize/`, {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//           Authorization: `Bearer ${token}`,
//         },
//       });

//       if (!response.ok) {
//         throw new Error("Failed to initialize conversation");
//       }

//       const data = await response.json();
//       setSelectedConversationId(data.conversation_id);
//     } catch (error) {
//       console.error("Error initializing conversation:", error);
//     }
//   };

//   const navigate = useNavigate()
//   return (
//     <div className="min-h-screen bg-background">
//       <header className="border-b shadow-[0_4px_8px_rgb(131,169,210)]">
//         <div className="container mx-auto px-4 h-16 flex items-center justify-between">

//           <div className="flex items-center space-x-3">
//             {/* Logo Image */}
//             <img src={logoIcon} alt="Traible Logo" className="h-10 md:h-12" />

//             {/* Styled Tagline */}
//             <h2 className="text-3xl font-bold bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent">
//               Know Your Tribe
//             </h2>
//           </div>


//           <div className="flex items-center gap-4">
//             {isAuthenticated ? (
//               <>

//                 <Button onClick={handleSelectConversation} variant="ghost">
//                   <MessageSquare className="w-4 h-4 mr-2" />
//                   New Chat
//                 </Button>

//                 <Button
//                   variant="outline"
//                   onClick={() => { navigate("/"), localStorage.clear(), setIsAuthenticated(false) }}
//                 >
//                   <LogOut className="w-4 h-4 mr-2" />
//                   Logout
//                 </Button>
//               </>
//             ) : (

//               <Button onClick={() => { navigate("/auth") }}>Sign In</Button>

//             )}
//             <ModeToggle />
//           </div>
//         </div>
//       </header>

//       <main>{children}</main>
//     </div>
//   );
// }


import { Link } from "wouter";
import { Button } from "@/components/ui/button";
import { ModeToggle } from "@/components/ui/toggle-mode";
import { useRecoilState } from "recoil";
import { isAuthenticatedState } from "@/store/auth";
import { LogOut, MessageSquare } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { selectedConversationIdState } from "@/store/chat";
import logoIcon from "../../../assets/logo.jpg";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { useEffect, useState } from "react";

export default function MainLayout({ children }: { children: React.ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useRecoilState(isAuthenticatedState);
  const [selectedConversationId, setSelectedConversationId] = useRecoilState(selectedConversationIdState);
  const [logoutConfirm, setLogoutConfirm] = useState<boolean>(false);
  const url = import.meta.env.VITE_API_URL;
  console.log(url);

  const handleSelectConversation = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`${url}/api/conversations/initialize/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to initialize conversation");
      }

      const data = await response.json();
      setSelectedConversationId(data.conversation_id);
    } catch (error) {
      console.error("Error initializing conversation:", error);
    }
  };

  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.clear();
    setIsAuthenticated(false);
    navigate("/");
    setLogoutConfirm(false);
  };
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b shadow-[0_4px_8px_rgb(131,169,210)]">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {/* Logo Image */}
            <img src={logoIcon} alt="Traible Logo" className="h-10 md:h-12" />

            {/* Styled Tagline */}
            <h2 className="text-3xl font-bold bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent">
              Know Your Tribe
            </h2>
          </div>

          <div className="flex items-center gap-4">
            {isAuthenticated ? (
              <>
                <Button onClick={handleSelectConversation} variant="ghost">
                  <MessageSquare className="w-4 h-4 mr-2" />
                  New Chat
                </Button>

                <Dialog open={logoutConfirm} onOpenChange={setLogoutConfirm}>
                  <DialogTrigger asChild>
                    <Button
                      variant="outline"
                      onClick={(e) => {

                        setLogoutConfirm(true);
                      }}
                    >
                      <LogOut className="w-4 h-4 mr-2" />
                      Logout
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-[425px] rounded-lg shadow-lg">
                    <DialogHeader>
                      <DialogTitle className="text-lg font-semibold text-primary">
                        Confirm Logout
                      </DialogTitle>
                      <DialogDescription className="text-sm text-gray-200">
                        Are you sure you want to log out? You will need to sign in again to access your account.
                      </DialogDescription>
                    </DialogHeader>
                    <DialogFooter className="mt-4">
                      <Button variant="outline" onClick={() => setLogoutConfirm(false)} className="text-primary hover:bg-primary">
                        Cancel
                      </Button>
                      <Button variant="destructive" onClick={handleLogout} className="bg-red-600 hover:bg-red-700 text-white">
                        Logout
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </>
            ) : (
              <Button onClick={() => navigate("/auth")}>Sign In</Button>
            )}
            <ModeToggle />
          </div>
        </div>
      </header>

      <main>{children}</main>
    </div>
  );
}