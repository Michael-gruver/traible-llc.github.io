import React, { useEffect, useState } from "react";
import { Toast, ToastProvider, ToastTitle, ToastDescription } from "@/components/ui/toast";
import { useToast } from "@/hooks/use-toast";


const OfflineAlert: React.FC = () => {
  const [isOffline, setIsOffline] = useState(!navigator.onLine);
  const { toast } = useToast();

  useEffect(() => {
    const handleOffline = () => {
      setIsOffline(true);
      toast({
        title: "You are offline!",
        description: "Check your internet connection.",
        variant: "destructive",
      });
    };

    const handleOnline = () => setIsOffline(false);

    window.addEventListener("offline", handleOffline);
    window.addEventListener("online", handleOnline);

    return () => {
      window.removeEventListener("offline", handleOffline);
      window.removeEventListener("online", handleOnline);
    };
  }, [toast]);

  return (
    <ToastProvider>
      {isOffline && (
        <Toast variant="destructive">
          <ToastTitle>You are offline!</ToastTitle>
          <ToastDescription>Check your internet connection.</ToastDescription>
        </Toast>
      )}
    </ToastProvider>
  );
};

export default OfflineAlert;