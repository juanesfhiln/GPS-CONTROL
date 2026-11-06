
import { Navigate, Route, Routes } from "react-router";
import { useState } from "react";

import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";

import ChangePasswordForm from "./features/auth/components/ChangePasswordForm";
import { useAuth } from "./features/auth/context/AuthContext";

function RutaProtegida() {
  const {
    autenticado,
    cargandoSesion,
    usuario,
    cerrarSesion
  } = useAuth();

  const [error, setError] = useState("");

  if (cargandoSesion) {
    return <p>Verificando sesión...</p>;
  }

  if (!autenticado) {
    return <Navigate to="/login" replace />;
  }

  // Obligar al usuario a cambiar su contraseña.
  if (usuario?.cambiar_password) {
    return (
      <main>
        <ChangePasswordForm />

        <button
          onClick={async () => {
            try {
              await cerrarSesion();
            } catch {
              setError("No se pudo cerrar la sesión en el servidor.");
            }
          }}
        >
          Cerrar sesión
        </button>

        {error && <p role="alert">{error}</p>}
      </main>
    );
  }

  async function salir() {
    try {
      await cerrarSesion();
    } catch {
      setError("No se pudo cerrar la sesión en el servidor.");
    }
  }

  return (
    <main>
      <h1>Dashboard GPS Control</h1>

      <p>Bienvenido, {usuario?.nombre}</p>

      <button onClick={salir}>
        Cerrar sesión
      </button>

      {error && <p role="alert">{error}</p>}
    </main>
  );
}

function App() {
  const { autenticado, cargandoSesion } = useAuth();

  if (cargandoSesion) {
    return <p>Verificando sesión...</p>;
  }

  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />

      <Route
        path="/login"
        element={
          autenticado
            ? <Navigate to="/dashboard" replace />
            : <LoginPage />
        }
      />

      <Route
        path="/dashboard"
        element={<RutaProtegida />}
      />

      <Route
        path="*"
        element={<Navigate to="/" replace />}
      />
    </Routes>
  );
}

export default App;
