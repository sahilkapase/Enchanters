import { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { agentLogin, agentLogout } from '../services/api';

const AuthCtx = createContext(null);
export const useAgent = () => useContext(AuthCtx);

export function AgentAuthProvider({ children }) {
  const [agent, setAgent] = useState(() => {
    const stored = localStorage.getItem('agent');
    return stored ? JSON.parse(stored) : null;
  });

  const login = useCallback(async (credentials) => {
    const payload = { phone: credentials.username, password: credentials.password };
    const data = await agentLogin(payload);
    localStorage.setItem('agent_access_token', data.access_token);
    localStorage.setItem('agent_refresh_token', data.refresh_token);
    localStorage.setItem('agent', JSON.stringify(data.agent));
    setAgent(data.agent);
  }, []);

  const logout = useCallback(async () => {
    try { await agentLogout(); } catch { /* ignore */ }
    localStorage.removeItem('agent_access_token');
    localStorage.removeItem('agent_refresh_token');
    localStorage.removeItem('agent');
    setAgent(null);
  }, []);

  const isAuthenticated = !!agent;

  return (
    <AuthCtx.Provider value={{ agent, isAuthenticated, login, logout }}>
      {children}
    </AuthCtx.Provider>
  );
}
