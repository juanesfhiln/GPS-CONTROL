
import { useEffect, useState } from "react";
import { getAuditLogs } from "../features/audit/services/auditService";
import type { AuditLog } from "../features/audit/types/audit";
import "../features/audit/styles/audit.scss";
import { useAuth } from "../features/auth/context/AuthContext";

function AuditPage() {
    const [registros, setRegistros] = useState<AuditLog[]>([]);
    const [pagina, setPagina] = useState(1);
    const [total, setTotal] = useState(0);
    const [totalPaginas, setTotalPaginas] = useState(0);
    const [usuarioId, setUsuarioId] = useState("");
    const [modulo, setModulo] = useState("");
    const [resultado, setResultado] = useState("");
    const [cargando, setCargando] = useState(true);
    const [error, setError] = useState("");
    const { usuario } = useAuth();
    const esAdministrador = usuario?.rol === "Administrador";

    useEffect(() => {

        if (!esAdministrador) return;

        let activo = true;

        async function cargarRegistros() {
            try {
                setCargando(true);
                setError("");

                const respuesta = await getAuditLogs({
                    pagina,
                    limite: 20,
                    usuario_id: usuarioId ? Number(usuarioId) : undefined,
                    modulo: modulo || undefined,
                    resultado: resultado || undefined
                });

                if (!activo) return;

                setRegistros(respuesta.resultados);
                setTotal(respuesta.total);
                setTotalPaginas(respuesta.total_paginas);
            } catch {
                if (activo) {
                    setError("No fue posible cargar los registros de auditoría.");
                }
            } finally {
                if (activo) setCargando(false);
            }
        }

        cargarRegistros();

        return () => {
            activo = false;
        };
    }, [pagina, usuarioId, modulo, resultado, esAdministrador]);

    function limpiarFiltros() {
        setUsuarioId("");
        setModulo("");
        setResultado("");
        setPagina(1);
    }

    function formatearFecha(fecha: string) {
        return new Date(fecha).toLocaleString("es-CO", {
            dateStyle: "short",
            timeStyle: "medium"
        });
    }

    function formatearAccion(accion: string) {
        const acciones: Record<string, string> = {
            LOGIN: "Inicio de sesión",
            LOGOUT: "Cierre de sesión",
            CHANGE_PASSWORD: "Cambio de contraseña",
            CREATE: "Creación",
            UPDATE: "Actualización",
            DELETE: "Eliminación",
            CHANGE_STATUS: "Cambio de estado",
            RESET_PASSWORD: "Restablecimiento de contraseña",
            ASSIGN: "Asignación",
            UNASSIGN: "Desvinculación"
        };

        return acciones[accion] || accion;
    }

    if (!esAdministrador) {
        return (
            <section className="audit-page">
                <p className="audit-page__error" role="alert">
                    No tienes permisos para consultar los registros de auditoría.
                </p>
            </section>
        );
    }
    
    return (
        <section className="audit-page">
            <div className="audit-page__heading">
                <div>
                    <span className="audit-page__eyebrow">
                        ADMINISTRACIÓN
                    </span>
                    <h1>Auditoría del sistema</h1>
                    <p>
                        Consulta y supervisa las actividades realizadas
                        dentro de GPS Control.
                    </p>
                </div>

                <div className="audit-page__total">
                    <span>Total de registros</span>
                    <strong>{total}</strong>
                </div>
            </div>

            <div className="audit-page__filters">
                <div className="audit-page__field">
                    <label htmlFor="audit-user">ID de usuario</label>
                    <input
                        id="audit-user"
                        type="number"
                        min="1"
                        placeholder="Ej. 1"
                        value={usuarioId}
                        onChange={(e) => {
                            setUsuarioId(e.target.value);
                            setPagina(1);
                        }}
                    />
                </div>

                <div className="audit-page__field">
                    <label htmlFor="audit-module">Módulo</label>
                    <select
                        id="audit-module"
                        value={modulo}
                        onChange={(e) => {
                            setModulo(e.target.value);
                            setPagina(1);
                        }}
                    >
                        <option value="">Todos los módulos</option>
                        <option value="AUTENTICACION">Autenticación</option>
                        <option value="USUARIOS">Usuarios</option>
                        <option value="CONDUCTORES">Conductores</option>
                        <option value="PASAJEROS">Pasajeros</option>
                    </select>
                </div>

                <div className="audit-page__field">
                    <label htmlFor="audit-result">Resultado</label>
                    <select
                        id="audit-result"
                        value={resultado}
                        onChange={(e) => {
                            setResultado(e.target.value);
                            setPagina(1);
                        }}
                    >
                        <option value="">Todos los resultados</option>
                        <option value="EXITOSO">Exitoso</option>
                        <option value="FALLIDO">Fallido</option>
                    </select>
                </div>

                <button
                    type="button"
                    className="audit-page__clear"
                    onClick={limpiarFiltros}
                >
                    Limpiar filtros
                </button>
            </div>

            {error && (
                <div className="audit-page__error">
                    {error}
                </div>
            )}

            <div className="audit-page__table-container">
                {cargando ? (
                    <p className="audit-page__message">
                        Cargando registros...
                    </p>
                ) : registros.length === 0 ? (
                    <p className="audit-page__message">
                        No se encontraron registros de auditoría.
                    </p>
                ) : (
                    <table className="audit-page__table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Usuario</th>
                                <th>Acción</th>
                                <th>Módulo</th>
                                <th>Descripción</th>
                                <th>Resultado</th>
                                <th>Dirección IP</th>
                                <th>Fecha</th>
                            </tr>
                        </thead>

                        <tbody>
                            {registros.map((registro) => (
                                <tr key={registro.id}>
                                    <td>{registro.id}</td>
                                    <td>{registro.usuario_id ?? "No identificado"}</td>
                                    <td>{formatearAccion(registro.accion)}</td>
                                    <td>{registro.modulo}</td>
                                    <td>{registro.descripcion}</td>
                                    <td>
                                        <span className={`audit-page__status audit-page__status--${registro.resultado.toLowerCase()}`}>
                                            {registro.resultado}
                                        </span>
                                    </td>
                                    <td>{registro.direccion_ip ?? "No disponible"}</td>
                                    <td>{formatearFecha(registro.fecha)}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>

            <div className="audit-page__pagination">
                <span>
                    Página {pagina} de {totalPaginas}
                </span>

                <div>
                    <button
                        type="button"
                        disabled={pagina <= 1 || cargando}
                        onClick={() => setPagina((actual) => actual - 1)}
                    >
                        Anterior
                    </button>

                    <button
                        type="button"
                        disabled={pagina >= totalPaginas || cargando}
                        onClick={() => setPagina((actual) => actual + 1)}
                    >
                        Siguiente
                    </button>
                </div>
            </div>
        </section>
    );
}

export default AuditPage;
