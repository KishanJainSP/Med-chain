import { createContext, useContext, useEffect, useState } from 'react';

const STORAGE_KEY = 'medchain_auth_v1';

const defaultState = {
  authenticated: false,
  userType: null, // 'institution', 'doctor', 'patient'
  wallet: null,
  userId: null,
  userData: null,
};

const AuthContext = createContext(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [state, setState] = useState(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : defaultState;
    } catch {
      return defaultState;
    }
  });

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }, [state]);

  const setAuth = (updates = {}) => {
    const next = { ...state, ...updates };
    setState(next);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  };

  const logout = () => {
    setState(defaultState);
    localStorage.removeItem(STORAGE_KEY);
  };

  return (
    <AuthContext.Provider value={{ state, setAuth, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
