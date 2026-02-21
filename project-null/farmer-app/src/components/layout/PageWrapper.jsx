import { useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import Sidebar from './Sidebar';
import { PageLoader } from '../common/Loader';

/**
 * Wraps protected pages with collapsible sidebar and auth guard.
 */
export default function PageWrapper({ children, requireAuth = true }) {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();
  const [expanded, setExpanded] = useState(true);

  if (loading) return <PageLoader />;

  if (requireAuth && !isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return (
    <>
      <Sidebar expanded={expanded} setExpanded={setExpanded} />
      <main
        className={`min-h-screen bg-gray-50 transition-all duration-300 ease-in-out
                    ${expanded ? 'md:ml-60' : 'md:ml-[68px]'}`}
      >
        {children}
      </main>
    </>
  );
}
