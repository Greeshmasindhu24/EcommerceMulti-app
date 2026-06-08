import React, { createContext, useState, useEffect } from 'react';
import { loginUser, registerUser, saveAuthSession, clearAuthStorage } from '../api';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedEmail = localStorage.getItem('email');
    const storedToken = localStorage.getItem('token');
    if (storedEmail && storedToken) {
      setUser({ email: storedEmail, token: storedToken });
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    const data = await loginUser(email, password);
    const session = { email: data.email || email, token: data.access_token };
    saveAuthSession(data.access_token, session.email);
    setUser(session);
    localStorage.setItem('user', JSON.stringify(session));
  };

  const register = async (name, email, password) => {
    await registerUser(email, password);
    await login(email, password);
  };

  const logout = () => {
    setUser(null);
    clearAuthStorage();
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
