import { useState, useEffect, lazy, Suspense } from "react";
import { HashRouter as Router, Routes, Route } from "react-router-dom";
import { Toaster } from "@/components/ui/toaster";
import { RecoilRoot } from "recoil";
import { ThemeProvider } from "@/components/ui/theme-provider";
import MainLayout from "@/components/layout/main-layout";
import TraibleLoader from "./components/TraibleLoader";
import OfflineAlert from "./components/OfflineAlert";


// Lazy load pages
const Home = lazy(() => import("@/pages/home"));
const Auth = lazy(() => import("@/pages/auth"));
const Chat = lazy(() => import("@/pages/chat"));
const NotFound = lazy(() => import("@/pages/not-found"));

function App() {
  return (
    <RecoilRoot>
      <ThemeProvider defaultTheme="dark">
      <OfflineAlert />
        <Router>
          <MainLayout>
            <Suspense fallback={
              <div className="w-full h-screen">
                <TraibleLoader
                  size="medium"
                  customMessages={{
                    initial: "Loading Traible",
                    middle: "Preparing Interface",
                    final: "Almost Ready",
                    complete: "Ready"
                  }}
                />
              </div>
            }>
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/auth" element={<Auth />} />
                <Route path="/chat" element={<Chat />} />
                <Route path="*" element={<NotFound />} />
              </Routes>
            </Suspense>
          </MainLayout>
        </Router>
        <Toaster />
      </ThemeProvider>
    </RecoilRoot>
  );
}

export default App;