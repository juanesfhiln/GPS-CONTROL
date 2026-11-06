
import { useState, type FormEvent } from "react";

import { useAuth } from "../context/AuthContext";
import {
  cambiarPassword,
  getCurrentUser
} from "../services/authService";

export default function ChangePasswordForm() {
  const { actualizarUsuario } = useAuth();

  const [passwordActual, setPasswordActual] = useState("");
  const [passwordNueva, setPasswordNueva] = useState("");
  const [confirmarPassword, setConfirmarPassword] = useState("");

  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");

  async function manejarCambioPassword(
    evento: FormEvent<HTMLFormElement>
  ) {
    evento.preventDefault();

    setError("");
    setMensaje("");

    if (passwordNueva.length < 12) {
      setError("La nueva contraseña debe tener al menos 12 caracteres.");
      return;
    }

    if (passwordNueva !== confirmarPassword) {
      setError("Las contraseñas nuevas no coinciden.");
      return;
    }

    if (passwordActual === passwordNueva) {
      setError("La nueva contraseña debe ser diferente a la actual.");
      return;
    }

    setCargando(true);

    try {
      await cambiarPassword({
        password_actual: passwordActual,
        password_nueva: passwordNueva,
        confirmar_password: confirmarPassword
      });

      const usuarioActualizado = await getCurrentUser();

      actualizarUsuario(usuarioActualizado);

      setPasswordActual("");
      setPasswordNueva("");
      setConfirmarPassword("");

      setMensaje("Contraseña actualizada correctamente.");
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "No fue posible actualizar la contraseña."
      );
    } finally {
      setCargando(false);
    }
  }

  return (
    <form onSubmit={manejarCambioPassword}>
      <h2>Cambiar contraseña</h2>

      <p>
        Debes actualizar tu contraseña antes de continuar.
      </p>

      <div>
        <label htmlFor="passwordActual">
          Contraseña actual
        </label>

        <input
          id="passwordActual"
          type="password"
          value={passwordActual}
          onChange={(evento) => setPasswordActual(evento.target.value)}
          autoComplete="current-password"
          required
        />
      </div>

      <div>
        <label htmlFor="passwordNueva">
          Nueva contraseña
        </label>

        <input
          id="passwordNueva"
          type="password"
          value={passwordNueva}
          onChange={(evento) => setPasswordNueva(evento.target.value)}
          autoComplete="new-password"
          minLength={12}
          maxLength={128}
          required
        />
      </div>

      <div>
        <label htmlFor="confirmarPassword">
          Confirmar nueva contraseña
        </label>

        <input
          id="confirmarPassword"
          type="password"
          value={confirmarPassword}
          onChange={(evento) => setConfirmarPassword(evento.target.value)}
          autoComplete="new-password"
          minLength={12}
          maxLength={128}
          required
        />
      </div>

      {error && <p role="alert">{error}</p>}

      {mensaje && <p role="status">{mensaje}</p>}

      <button type="submit" disabled={cargando}>
        {cargando ? "Actualizando..." : "Actualizar contraseña"}
      </button>
    </form>
  );
}
