import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import { DocumentProvider } from "./contexts/DocumentContext";
import { ChatProvider } from "./contexts/ChatContext";
import Index from "./pages/Index";
import ApiTest from "./pages/ApiTest";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <DocumentProvider>
        <ChatProvider>
          <Toaster />
          <Sonner />
          <BrowserRouter>
            <div className="fixed top-0 left-0 right-0 bg-background border-b z-10 p-2 flex gap-4">
              <Link to="/" className="text-sm font-medium hover:underline">Home</Link>
              <Link to="/api-test" className="text-sm font-medium hover:underline">API Test</Link>
            </div>
            <div className="pt-12">
              <Routes>
                <Route path="/" element={<Index />} />
                <Route path="/api-test" element={<ApiTest />} />
                {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
                <Route path="*" element={<NotFound />} />
              </Routes>
            </div>
          </BrowserRouter>
        </ChatProvider>
      </DocumentProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
