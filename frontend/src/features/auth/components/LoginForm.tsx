
import { useState, type SyntheticEvent } from "react";
import { useAuth } from "../context/AuthContext";

export default function LoginForm() {
  const { iniciarSesion } = useAuth();

  const [correo, setCorreo] = useState("");
  const [password, setPassword] = useState("");
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");

  async function manejarInicioSesion(
    evento: SyntheticEvent<HTMLFormElement>
  ) {
    evento.preventDefault();

    setError("");
    setMensaje("");
    setCargando(true);

    try {
      await iniciarSesion({ correo, password });

      setMensaje("Sesión iniciada correctamente.");
      setPassword("");
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Ocurrió un error inesperado."
      );
    } finally {
      setCargando(false);
    }
  }

  return (
    <form onSubmit={manejarInicioSesion}>
      <div>
        <label htmlFor="correo">Correo electrónico</label>

        <input
          id="correo"
          type="email"
          value={correo}
          onChange={(evento) => setCorreo(evento.target.value)}
          placeholder="usuario@ejemplo.com"
          autoComplete="username"
          required
        />
      </div>

      <div>
        <label htmlFor="password">Contraseña</label>

        <input
          id="password"
          type="password"
          value={password}
          onChange={(evento) => setPassword(evento.target.value)}
          placeholder="Ingresa tu contraseña"
          autoComplete="current-password"
          required
        />
      </div>

      {error && (
        <p role="alert">{error}</p>
      )}

      {mensaje && (
        <p role="status">{mensaje}</p>
      )}

      <button type="submit" disabled={cargando}>
        {cargando ? "Iniciando sesión..." : "Iniciar sesión"}
      </button>
    </form>
  );
}
