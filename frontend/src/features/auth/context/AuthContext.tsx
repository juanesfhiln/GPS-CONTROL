
import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode
} from "react";

import {
  login as loginService,
  logout as logoutService,
  getCurrentUser
} from "../services/authService";

import type {
  LoginRequest,
  AuthUser
} from "../types/auth";

interface AuthContextType {
  usuario: AuthUser | null;
  autenticado: boolean;
  cargandoSesion: boolean;
  iniciarSesion: (datos: LoginRequest) => Promise<void>;
  cerrarSesion: () => Promise<void>;
  actualizarUsuario: (usuario: AuthUser) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [usuario, setUsuario] = useState<AuthUser | null>(null);
  const [cargandoSesion, setCargandoSesion] = useState(true);

  useEffect(() => {
    let activo = true;

    async function restaurarSesion() {
      try {
        const usuarioActual = await getCurrentUser();

        if (activo) {
          setUsuario(usuarioActual);
        }
      } catch {
        if (activo) {
          setUsuario(null);
        }
      } finally {
        if (activo) {
          setCargandoSesion(false);
        }
      }
    }

    void restaurarSesion();

    return () => {
      activo = false;
    };
  }, []);

  async function iniciarSesion(datos: LoginRequest): Promise<void> {
    await loginService(datos);

    const usuarioActual = await getCurrentUser();

    setUsuario(usuarioActual);
    setCargandoSesion(false);
  }

  async function cerrarSesion(): Promise<void> {
    await logoutService();
    setUsuario(null);
  }

  function actualizarUsuario(usuarioActualizado: AuthUser): void {
    setUsuario(usuarioActualizado);
  }

  const valor: AuthContextType = {
    usuario,
    autenticado: usuario !== null,
    cargandoSesion,
    iniciarSesion,
    cerrarSesion,
    actualizarUsuario
  };

  return (
    <AuthContext.Provider value={valor}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const contexto = useContext(AuthContext);

  if (!contexto) {
    throw new Error(
      "useAuth debe utilizarse dentro de AuthProvider"
    );
  }

  return contexto;
}
