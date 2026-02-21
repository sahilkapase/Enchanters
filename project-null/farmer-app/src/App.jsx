import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';

import { AuthProvider } from './context/AuthContext';
import { LanguageProvider } from './context/LanguageContext';
import PageWrapper from './components/layout/PageWrapper';

/* ── Pages ── */
import Landing from './pages/Landing';
import Signup from './pages/Signup';
import Login from './pages/Login';
import Home from './pages/Home';
import Schemes from './pages/Schemes';
import SchemeDetail from './pages/SchemeDetail';
import Insurance from './pages/Insurance';
import Subsidies from './pages/Subsidies';
import Notifications from './pages/Notifications';
import Profile from './pages/Profile';

/* ── React-Query client ── */
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000,     // 5 min default
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <LanguageProvider>
          <AuthProvider>
            {/* ── Public routes (no auth required) ── */}
            <Routes>
              <Route path="/" element={<Landing />} />
              <Route path="/signup" element={<Signup />} />
              <Route path="/login" element={<Login />} />

              {/* ── Protected routes (wrapped with PageWrapper) ── */}
              <Route path="/home" element={<PageWrapper><Home /></PageWrapper>} />
              <Route path="/schemes" element={<PageWrapper><Schemes /></PageWrapper>} />
              <Route path="/schemes/:id" element={<PageWrapper><SchemeDetail /></PageWrapper>} />
              <Route path="/insurance" element={<PageWrapper><Insurance /></PageWrapper>} />
              <Route path="/subsidies" element={<PageWrapper><Subsidies /></PageWrapper>} />
              <Route path="/notifications" element={<PageWrapper><Notifications /></PageWrapper>} />
              <Route path="/profile" element={<PageWrapper><Profile /></PageWrapper>} />

              {/* ── Fallback ── */}
              <Route path="*" element={<Landing />} />
            </Routes>

            <Toaster
              position="top-center"
              toastOptions={{
                duration: 3000,
                style: { fontSize: '14px', borderRadius: '8px' },
                success: { iconTheme: { primary: '#16a34a', secondary: '#fff' } },
                error: { iconTheme: { primary: '#dc2626', secondary: '#fff' } },
              }}
            />
          </AuthProvider>
        </LanguageProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
