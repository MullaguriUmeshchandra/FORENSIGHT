import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    try {
      const savedUser = localStorage.getItem('forensics_user');
      return savedUser ? JSON.parse(savedUser) : null;
    } catch {
      return null;
    }
  });

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('forensics_token');

    if (!token) {
      setLoading(false);
      return;
    }

    authAPI.me()
      .then((res) => {
        setUser(res.data);
        localStorage.setItem(
          'forensics_user',
          JSON.stringify(res.data)
        );
      })
      .catch((err) => {
        // Only clear auth on actual 401 Unauthorized, not temporary network latency or cold-start
        if (err.response && err.response.status === 401) {
          localStorage.removeItem('forensics_token');
          localStorage.removeItem('forensics_user');
          setUser(null);
        }
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const login = async (username, password) => {
    const res = await authAPI.login(username, password);

    const { access_token, user: userData } = res.data;

    localStorage.setItem('forensics_token', access_token);
    localStorage.setItem(
      'forensics_user',
      JSON.stringify(userData)
    );

    setUser(userData);

    return userData;
  };

  const register = async (userData) => {
    const res = await authAPI.register(userData);
    return res.data;
  };

  const logout = () => {
    localStorage.removeItem('forensics_token');
    localStorage.removeItem('forensics_user');
    setUser(null);
  };

  const isAdmin = user?.role === 'Admin';

  const isInvestigator =
    user?.role === 'Investigator' ||
    user?.role === 'Admin';

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        logout,
        isAdmin,
        isInvestigator,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error(
      'useAuth must be used within an AuthProvider'
    );
  }

  return context;
};