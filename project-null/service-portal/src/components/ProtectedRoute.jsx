import { Navigate } from 'react-router-dom';
import { useAgent } from '../context/AgentAuthContext';

export default function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAgent();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return children;
}
