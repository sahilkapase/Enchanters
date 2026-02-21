import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authApi } from '../services/authApi';
import { farmerApi } from '../services/farmerApi';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [farmer, setFarmer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check for existing session on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const savedFarmer = localStorage.getItem('farmer');

    if (token && savedFarmer) {
      try {
        setFarmer(JSON.parse(savedFarmer));
        setIsAuthenticated(true);
      } catch {
        clearSession();
      }
    }
    setLoading(false);
  }, []);

  const clearSession = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('farmer');
    setFarmer(null);
    setIsAuthenticated(false);
  }, []);

  /**
   * After OTP verification during login, store tokens and fetch farmer profile.
   */
  const loginWithTokens = useCallback(async (data) => {
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);

    try {
      const res = await farmerApi.getMe();
      const farmerData = res.data;
      localStorage.setItem('farmer', JSON.stringify(farmerData));
      setFarmer(farmerData);
      setIsAuthenticated(true);
      return farmerData;
    } catch (err) {
      clearSession();
      throw err;
    }
  }, [clearSession]);

  /**
   * After signup, we may get the farmer data directly without fetching.
   */
  const setFarmerAfterSignup = useCallback((farmerData, tokens) => {
    if (tokens) {
      localStorage.setItem('access_token', tokens.access_token);
      localStorage.setItem('refresh_token', tokens.refresh_token);
    }
    localStorage.setItem('farmer', JSON.stringify(farmerData));
    setFarmer(farmerData);
    setIsAuthenticated(true);
  }, []);

  /**
   * Refresh farmer data from server
   */
  const refreshFarmer = useCallback(async () => {
    try {
      const res = await farmerApi.getMe();
      const farmerData = res.data;
      localStorage.setItem('farmer', JSON.stringify(farmerData));
      setFarmer(farmerData);
      return farmerData;
    } catch (err) {
      console.error('Failed to refresh farmer data:', err);
      throw err;
    }
  }, []);

  /**
   * Logout
   */
  const logout = useCallback(async () => {
    try {
      await authApi.logout();
    } catch {
      // ignore logout API errors
    } finally {
      clearSession();
    }
  }, [clearSession]);

  /**
   * Update local farmer state (after profile edits)
   */
  const updateFarmerLocal = useCallback((updates) => {
    setFarmer((prev) => {
      const updated = { ...prev, ...updates };
      localStorage.setItem('farmer', JSON.stringify(updated));
      return updated;
    });
  }, []);

  const value = {
    farmer,
    loading,
    isAuthenticated,
    loginWithTokens,
    setFarmerAfterSignup,
    refreshFarmer,
    logout,
    updateFarmerLocal,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
