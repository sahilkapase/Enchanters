import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';

import { AgentAuthProvider } from './context/AgentAuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import AppShell from './components/AppShell';

import AgentLogin from './pages/AgentLogin';
import Dashboard from './pages/Dashboard';
import FarmerLookup from './pages/FarmerLookup';
import FarmerView from './pages/FarmerView';
import ActivityLog from './pages/ActivityLog';
import ReviewQueue from './pages/ReviewQueue';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, refetchOnWindowFocus: false, staleTime: 2 * 60 * 1000 },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AgentAuthProvider>
          <Routes>
            <Route path="/login" element={<AgentLogin />} />

            {/* Protected shell */}
            <Route element={<ProtectedRoute><AppShell /></ProtectedRoute>}>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/review" element={<ReviewQueue />} />
              <Route path="/lookup" element={<FarmerLookup />} />
              <Route path="/farmer/:farmerId" element={<FarmerView />} />
              <Route path="/activity" element={<ActivityLog />} />
            </Route>

            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>

          <Toaster
            position="top-center"
            toastOptions={{
              duration: 3000,
              style: { fontSize: '14px', borderRadius: '8px' },
            }}
          />
        </AgentAuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
