
import { useState, type FormEvent } from "react";
import { useAuth } from "../context/AuthContext";

export default function LoginForm() {
    const { iniciarSesion } = useAuth();

    const [correo, setCorreo] = useState("");
    const [password, setPassword] = useState("");
    const [cargando, setCargando] = useState(false);
    const [error, setError] = useState("");

    async function manejarInicioSesion(
        evento: FormEvent<HTMLFormElement>
    ) {
        evento.preventDefault();
        setError("");
        setCargando(true);

        try {
            await iniciarSesion({ correo, password });
            setPassword("");
        } catch (error) {
            setError(
                error instanceof Error
                    ? error.message
                    : "No fue posible iniciar sesión."
            );
        } finally {
            setCargando(false);
        }
    }

    return (
        <form
            className="login-page__form"
            onSubmit={manejarInicioSesion}
        >
            <div className="login-page__form-field">
                <label htmlFor="correo">
                    Correo electrónico
                </label>

                <input
                    id="correo"
                    type="email"
                    value={correo}
                    onChange={(evento) => setCorreo(evento.target.value)}
                    placeholder="usuario@ejemplo.com"
                    autoComplete="username"
                    disabled={cargando}
                    required
                />
            </div>

            <div className="login-page__form-field">
                <label htmlFor="password">
                    Contraseña
                </label>

                <input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(evento) => setPassword(evento.target.value)}
                    placeholder="Ingresa tu contraseña"
                    autoComplete="current-password"
                    disabled={cargando}
                    required
                />
            </div>

            {error && (
                <p role="alert">{error}</p>
            )}

            <button type="submit" disabled={cargando}>
                {cargando ? "Iniciando sesión..." : "Iniciar sesión"}
            </button>
        </form>
    );
}
