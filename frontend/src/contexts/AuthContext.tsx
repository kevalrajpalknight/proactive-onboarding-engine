import { createContext, useContext, useState, type ReactNode } from "react";
import {
  login as apiLogin,
  register as apiRegister,
  setAuthToken,
  type LoginRequest,
  type RegisterRequest,
  type UserResponse,
} from "../services/api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
interface AuthState {
  user: UserResponse | null;
  token: string | null;
  isAuthenticated: boolean;
}

interface AuthContextType extends AuthState {
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
}

// ---------------------------------------------------------------------------
// Persistence helpers
// ---------------------------------------------------------------------------
const STORAGE_KEY = "poe_auth";

function loadFromStorage(): { user: UserResponse; token: string } | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function saveToStorage(user: UserResponse, token: string) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ user, token }));
}

function clearStorage() {
  localStorage.removeItem(STORAGE_KEY);
}

// ---------------------------------------------------------------------------
// Context
// ---------------------------------------------------------------------------
const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>(() => {
    const stored = loadFromStorage();
    if (stored) {
      setAuthToken(stored.token);
      return { user: stored.user, token: stored.token, isAuthenticated: true };
    }
    return { user: null, token: null, isAuthenticated: false };
  });

  const login = async (data: LoginRequest) => {
    const response = await apiLogin(data);
    setAuthToken(response.token);
    saveToStorage(response.user, response.token);
    setState({
      user: response.user,
      token: response.token,
      isAuthenticated: true,
    });
  };

  const register = async (data: RegisterRequest) => {
    await apiRegister(data);
    // Auto-login after successful registration
    await login({ email: data.email, password: data.password });
  };

  const logout = () => {
    setAuthToken(null);
    clearStorage();
    setState({ user: null, token: null, isAuthenticated: false });
  };

  return (
    <AuthContext.Provider value={{ ...state, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
