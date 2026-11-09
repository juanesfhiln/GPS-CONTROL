import { useEffect, useState, type SyntheticEvent } from "react";

import { useAuth } from "../features/auth/context/AuthContext";

import {
    listarUsuarios,
    listarRoles,
    crearUsuario,
    actualizarUsuario,
    cambiarEstadoUsuario,
    restablecerPasswordUsuario
} from "../features/users/services/userService";

import type {
    User,
    Role,
    UserCreate,
    UserUpdate
} from "../features/users/types/user";

import "../features/users/styles/users.scss";

const formularioInicial = {
    nombre: "",
    correo: "",
    password: "",
    rol_id: ""
};

function UsersPage() {
    const { usuario } = useAuth();

    const [usuarioConfirmacion, setUsuarioConfirmacion] = useState<User | null>(null);
    const [procesandoEstado, setProcesandoEstado] = useState(false);
    const [usuarios, setUsuarios] = useState<User[]>([]);
    const [roles, setRoles] = useState<Role[]>([]);

    const [formulario, setFormulario] = useState(formularioInicial);
    const [usuarioSeleccionado, setUsuarioSeleccionado] = useState<User | null>(null);

    const [mostrarFormulario, setMostrarFormulario] = useState(false);
    const [cargando, setCargando] = useState(true);
    const [guardando, setGuardando] = useState(false);

    const [error, setError] = useState("");
    const [mensaje, setMensaje] = useState("");

    const esAdministrador = usuario?.rol === "Administrador";

    const [usuarioReset, setUsuarioReset] = useState<User | null>(null);
    const [passwordTemporal, setPasswordTemporal] = useState("");
    const [procesandoReset, setProcesandoReset] = useState(false);

    async function cargarDatos() {
        try {
            setCargando(true);
            setError("");

            const [usuariosRespuesta, rolesRespuesta] = await Promise.all([
                listarUsuarios(),
                listarRoles()
            ]);

            setUsuarios(usuariosRespuesta);
            setRoles(rolesRespuesta);
        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : "No fue posible cargar los usuarios."
            );
        } finally {
            setCargando(false);
        }
    }

    useEffect(() => {
        if (esAdministrador) {
            void cargarDatos();
        }
    }, [esAdministrador]);

    function abrirFormulario(usuarioEditar: User | null = null) {
        setError("");
        setMensaje("");
        setUsuarioSeleccionado(usuarioEditar);

        if (usuarioEditar) {
            const rol = roles.find(
                (item) => item.nombre === usuarioEditar.rol
            );

            setFormulario({
                nombre: usuarioEditar.nombre,
                correo: usuarioEditar.correo,
                password: "",
                rol_id: rol ? String(rol.id) : ""
            });
        } else {
            setFormulario(formularioInicial);
        }

        setMostrarFormulario(true);
    }

    function cerrarFormulario() {
        if (guardando) return;

        setMostrarFormulario(false);
        setUsuarioSeleccionado(null);
        setFormulario(formularioInicial);
    }

    function actualizarCampo(
        campo: keyof typeof formulario,
        valor: string
    ) {
        setFormulario((actual) => ({
            ...actual,
            [campo]: valor
        }));
    }

    async function guardarUsuario(evento: SyntheticEvent<HTMLFormElement>) {
        evento.preventDefault();

        if (!formulario.rol_id) {
            setError("Debes seleccionar un rol.");
            return;
        }

        try {
            setGuardando(true);
            setError("");
            setMensaje("");

            if (usuarioSeleccionado) {
                const datos: UserUpdate = {
                    nombre: formulario.nombre.trim(),
                    correo: formulario.correo.trim(),
                    rol_id: Number(formulario.rol_id)
                };

                await actualizarUsuario(usuarioSeleccionado.id, datos);
                setMensaje("Usuario actualizado correctamente.");
            } else {
                if (formulario.password.length < 8) {
                    setError("La contraseña debe tener al menos 8 caracteres.");
                    return;
                }

                const datos: UserCreate = {
                    nombre: formulario.nombre.trim(),
                    correo: formulario.correo.trim(),
                    password: formulario.password,
                    rol_id: Number(formulario.rol_id)
                };

                await crearUsuario(datos);
                setMensaje("Usuario creado correctamente.");
            }

            setMostrarFormulario(false);
            setUsuarioSeleccionado(null);
            setFormulario(formularioInicial);

            await cargarDatos();
        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : "No fue posible guardar el usuario."
            );
        } finally {
            setGuardando(false);
        }
    }

    async function gestionarEstado() {
        if (!usuarioConfirmacion) return;

        try {
            setProcesandoEstado(true);
            setError("");
            setMensaje("");

            await cambiarEstadoUsuario(usuarioConfirmacion.id);

            const accion = usuarioConfirmacion.activo ? "desactivado" : "activado";

            setMensaje(`Usuario ${accion} correctamente.`);
            setUsuarioConfirmacion(null);

            await cargarDatos();
        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : "No fue posible cambiar el estado del usuario."
            );
        } finally {
            setProcesandoEstado(false);
        }
    }

    async function confirmarRestablecimiento() {
        if (!usuarioReset) return;

        try {
            setProcesandoReset(true);
            setError("");
            setMensaje("");

            const respuesta = await restablecerPasswordUsuario(usuarioReset.id);

            setPasswordTemporal(respuesta.password_temporal);
            setUsuarioReset(null);

            await cargarDatos();
        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : "No fue posible restablecer la contraseña."
            );
        } finally {
            setProcesandoReset(false);
        }
    }

    if (!esAdministrador) {
        return (
            <section className="users-page">
                <p className="users-page__error" role="alert">
                    No tienes permisos para administrar usuarios.
                </p>
            </section>
        );
    }

    async function copiarPasswordTemporal() {
        try {
            await navigator.clipboard.writeText(passwordTemporal);
            setMensaje("Contraseña temporal copiada correctamente.");
        } catch {
            setError("No fue posible copiar la contraseña.");
        }
    }

    return (
        <section className="users-page">
            <header className="users-page__header">
                <div>
                    <h1>Gestión de usuarios</h1>
                    <p>
                        Administra las cuentas, los roles y los permisos de acceso.
                    </p>
                </div>

                <button
                    type="button"
                    onClick={() => abrirFormulario()}
                >
                    Nuevo usuario
                </button>
            </header>

            {error && (
                <p className="users-page__error" role="alert">
                    {error}
                </p>
            )}

            {mensaje && (
                <p className="users-page__success" role="status">
                    {mensaje}
                </p>
            )}

            {cargando ? (
                <p className="users-page__loading">
                    Cargando usuarios...
                </p>
            ) : usuarios.length === 0 ? (
                <p className="users-page__empty">
                    No hay usuarios registrados.
                </p>
            ) : (
                <div className="users-page__table-container">
                    <table className="users-table">
                        <thead>
                            <tr>
                                <th>Nombre</th>
                                <th>Correo</th>
                                <th>Rol</th>
                                <th>Estado</th>
                                <th>Contraseña pendiente</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>

                        <tbody>
                            {usuarios.map((usuarioItem) => (
                                <tr key={usuarioItem.id}>
                                    <td>{usuarioItem.nombre}</td>
                                    <td>{usuarioItem.correo}</td>
                                    <td>{usuarioItem.rol}</td>
                                    <td>
                                        <span
                                            className={`users-table__status ${
                                                usuarioItem.activo
                                                    ? "users-table__status--active"
                                                    : "users-table__status--inactive"
                                            }`}
                                        >
                                            {usuarioItem.activo ? "Activo" : "Inactivo"}
                                        </span>
                                    </td>
                                    <td>
                                        {usuarioItem.cambiar_password
                                            ? "Sí"
                                            : "No"}
                                    </td>
                                    <td className="users-table__actions">
                                        <button
                                            type="button"
                                            disabled={usuarioItem.id === usuario?.id || !usuarioItem.activo}
                                            onClick={() => setUsuarioReset(usuarioItem)}
                                        >
                                            Restablecer contraseña
                                        </button>

                                        <button
                                            type="button"
                                            disabled={usuarioItem.id === usuario?.id}
                                            onClick={() => setUsuarioConfirmacion(usuarioItem)}
                                        >
                                            {usuarioItem.activo
                                                ? "Desactivar"
                                                : "Activar"}
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {mostrarFormulario && (
                <div className="users-page__modal">
                    <form
                        className="user-form"
                        onSubmit={guardarUsuario}
                    >
                        <h2>
                            {usuarioSeleccionado
                                ? "Editar usuario"
                                : "Registrar usuario"}
                        </h2>

                        <label htmlFor="nombre">
                            Nombre
                        </label>

                        <input
                            id="nombre"
                            type="text"
                            minLength={2}
                            maxLength={100}
                            required
                            value={formulario.nombre}
                            onChange={(evento) =>
                                actualizarCampo("nombre", evento.target.value)
                            }
                        />

                        <label htmlFor="correo">
                            Correo electrónico
                        </label>

                        <input
                            id="correo"
                            type="email"
                            required
                            value={formulario.correo}
                            onChange={(evento) =>
                                actualizarCampo("correo", evento.target.value)
                            }
                        />

                        {!usuarioSeleccionado && (
                            <>
                                <label htmlFor="password">
                                    Contraseña inicial
                                </label>

                                <input
                                    id="password"
                                    type="password"
                                    minLength={8}
                                    required
                                    value={formulario.password}
                                    onChange={(evento) =>
                                        actualizarCampo("password", evento.target.value)
                                    }
                                />
                            </>
                        )}

                        <label htmlFor="rol">
                            Rol
                        </label>

                        <select
                            id="rol"
                            required
                            value={formulario.rol_id}
                            onChange={(evento) =>
                                actualizarCampo("rol_id", evento.target.value)
                            }
                        >
                            <option value="">
                                Selecciona un rol
                            </option>

                            {roles.map((rol) => (
                                <option
                                    key={rol.id}
                                    value={rol.id}
                                >
                                    {rol.nombre}
                                </option>
                            ))}
                        </select>

                        <div className="user-form__actions">
                            <button
                                type="button"
                                disabled={guardando}
                                onClick={cerrarFormulario}
                            >
                                Cancelar
                            </button>

                            <button
                                type="submit"
                                disabled={guardando}
                            >
                                {guardando
                                    ? "Guardando..."
                                    : "Guardar usuario"}
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {usuarioConfirmacion && (
                <div className="users-page__modal">
                    <div
                        className="users-confirmation"
                        role="alertdialog"
                        aria-modal="true"
                        aria-labelledby="confirmation-title"
                        aria-describedby="confirmation-description"
                    >
                        <div className="users-confirmation__icon">
                            !
                        </div>

                        <h2 id="confirmation-title">
                            {usuarioConfirmacion.activo
                                ? "Desactivar usuario"
                                : "Activar usuario"}
                        </h2>

                        <p id="confirmation-description">
                            {usuarioConfirmacion.activo
                                ? `¿Estás seguro de que deseas desactivar la cuenta de ${usuarioConfirmacion.nombre}?`
                                : `¿Deseas volver a activar la cuenta de ${usuarioConfirmacion.nombre}?`}
                        </p>

                        <div className="users-confirmation__actions">
                            <button
                                type="button"
                                disabled={procesandoEstado}
                                onClick={() => setUsuarioConfirmacion(null)}
                            >
                                Cancelar
                            </button>

                            <button
                                type="button"
                                disabled={procesandoEstado}
                                className={
                                    usuarioConfirmacion.activo
                                        ? "users-confirmation__danger"
                                        : "users-confirmation__success"
                                }
                                onClick={gestionarEstado}
                            >
                                {procesandoEstado
                                    ? "Procesando..."
                                    : usuarioConfirmacion.activo
                                        ? "Sí, desactivar"
                                        : "Sí, activar"}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {usuarioReset && (
                <div className="users-page__modal">
                    <div className="users-confirmation">
                        <div className="users-confirmation__icon">
                            !
                        </div>

                        <h2>Restablecer contraseña</h2>

                        <p>
                            ¿Deseas generar una nueva contraseña temporal para
                            <strong> {usuarioReset.nombre}</strong>?
                        </p>

                        <p>
                            La contraseña anterior dejará de funcionar y el usuario
                            tendrá que establecer una nueva al iniciar sesión.
                        </p>

                        <div className="users-confirmation__actions">
                            <button
                                type="button"
                                disabled={procesandoReset}
                                onClick={() => setUsuarioReset(null)}
                            >
                                Cancelar
                            </button>

                            <button
                                type="button"
                                className="users-confirmation__danger"
                                disabled={procesandoReset}
                                onClick={confirmarRestablecimiento}
                            >
                                {procesandoReset ? "Procesando..." : "Confirmar"}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {passwordTemporal && (
                <div className="users-page__modal">
                    <div className="users-confirmation">
                        <div className="users-confirmation__icon">
                            ✓
                        </div>

                        <h2>Contraseña restablecida</h2>

                        <p>
                            Comparte esta contraseña temporal con el usuario.
                            Solo se mostrará en esta ocasión.
                        </p>

                        <div className="users-confirmation__password">
                            <code>{passwordTemporal}</code>

                            <button
                                type="button"
                                onClick={copiarPasswordTemporal}
                            >
                                Copiar contraseña
                            </button>
                        </div>

                        <p>
                            El usuario deberá cambiarla al iniciar sesión.
                        </p>

                        <div className="users-confirmation__actions">
                            <button
                                type="button"
                                onClick={() => setPasswordTemporal("")}
                            >
                                Cerrar
                            </button>
                        </div>
                    </div>
                </div>
            )}

            
        </section>
    );
}

export default UsersPage;