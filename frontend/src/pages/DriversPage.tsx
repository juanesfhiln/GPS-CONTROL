
import { useEffect, useState } from "react";

import { useAuth } from "../features/auth/context/AuthContext";

import DriversTable from "../features/drivers/components/DriversTable";
import DriverForm from "../features/drivers/components/DriverForm";
import DriverAssignmentForm from "../features/drivers/components/DriverAssignmentForm";

import {
    getDrivers,
    createDriver,
    updateDriver,
    deleteDriver,
    assignDriver,
    unassignDriver
} from "../features/drivers/services/driverService";

import type {
    Driver,
    DriverPayload
} from "../features/drivers/types/driver";

function DriversPage() {
    const { usuario } = useAuth();

    const [conductores, setConductores] = useState<Driver[]>([]);
    const [pagina, setPagina] = useState(1);
    const [totalPaginas, setTotalPaginas] = useState(1);
    const [busqueda, setBusqueda] = useState("");
    const [filtro, setFiltro] = useState("");

    const [cargando, setCargando] = useState(true);
    const [guardando, setGuardando] = useState(false);
    const [error, setError] = useState("");

    const [mostrarFormulario, setMostrarFormulario] = useState(false);
    const [conductorSeleccionado, setConductorSeleccionado] = useState<Driver | null>(null);
    const [mensaje, setMensaje] = useState("");

    const puedeGestionar =
        usuario?.rol === "Admin" ||
        usuario?.rol === "Administrador" ||
        usuario?.rol === "Operador";

    const [conductorAsignacion, setConductorAsignacion] = useState<Driver | null>(null);

    const [guardandoAsignacion, setGuardandoAsignacion] = useState(false);

    async function cargarConductores() {
        try {
            setCargando(true);
            setError("");

            const respuesta = await getDrivers(pagina, 10, filtro);

            setConductores(respuesta.resultados);
            setTotalPaginas(respuesta.total_paginas);
        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : "No fue posible cargar los conductores."
            );
        } finally {
            setCargando(false);
        }
    }

    useEffect(() => {
        void cargarConductores();
    }, [pagina, filtro]);

    function abrirFormulario(conductor: Driver | null = null) {
        setConductorSeleccionado(conductor);
        setMostrarFormulario(true);
    }

    function cerrarFormulario() {
        if (guardando) return;

        setMostrarFormulario(false);
        setConductorSeleccionado(null);
    }

    function abrirAsignacion(conductor: Driver) {
        setConductorAsignacion(conductor);
    }

    async function gestionarAsignacion(
        driverId: number,
        unitId: number
    ) {
        try {
            setGuardandoAsignacion(true);
            setError("");
            setMensaje("");

            await assignDriver(driverId, unitId);

            setConductores((actuales) =>
                actuales.map((conductor) =>
                    conductor.id === driverId
                        ? { ...conductor, assigned_unit_id: unitId }
                        : conductor
                )
            );

            setConductorAsignacion(null);
            setMensaje("Conductor asignado correctamente.");
        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : "No fue posible asignar el vehículo."
            );
        } finally {
            setGuardandoAsignacion(false);
        }
    }


    async function gestionarDesvinculacion(
        driverId: number,
        unitId: number
    ) {
        try {
            setGuardandoAsignacion(true);
            setError("");
            setMensaje("");

            await unassignDriver(driverId, unitId);

            setConductores((actuales) =>
                actuales.map((conductor) =>
                    conductor.id === driverId
                        ? { ...conductor, assigned_unit_id: null }
                        : conductor
                )
            );

            setConductorAsignacion(null);
            setMensaje("Conductor desvinculado correctamente.");
        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : "No fue posible desvincular el vehículo."
            );
        } finally {
            setGuardandoAsignacion(false);
        }
    }

    async function guardarConductor(datos: DriverPayload) {
        try {
            setGuardando(true);
            setError("");

            if (conductorSeleccionado) {
                await updateDriver(conductorSeleccionado.id, datos);
            } else {
                await createDriver(datos);
            }

            setMostrarFormulario(false);
            setConductorSeleccionado(null);

            await cargarConductores();
        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : "No fue posible guardar el conductor."
            );
        } finally {
            setGuardando(false);
        }
    }

    async function eliminarConductor(conductor: Driver) {
        const confirmar = window.confirm(
            `¿Estás seguro de eliminar al conductor ${conductor.name}?`
        );

        if (!confirmar) return;

        try {
            setError("");

            await deleteDriver(conductor.id);

            await cargarConductores();
        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : "No fue posible eliminar el conductor."
            );
        }
    }

    function buscarConductores(evento: React.FormEvent<HTMLFormElement>) {
        evento.preventDefault();

        setPagina(1);
        setFiltro(busqueda.trim());
    }

    return (
        <section className="drivers-page">
            <header className="drivers-page__header">
                <div>
                    <h1>Gestión de conductores</h1>
                    <p>Consulta y administra los conductores registrados en Wialon.</p>
                </div>

                {puedeGestionar && (
                    <button onClick={() => abrirFormulario()}>
                        Nuevo conductor
                    </button>
                )}
            </header>

            <form
                className="drivers-page__search"
                onSubmit={buscarConductores}
            >
                <input
                    type="search"
                    placeholder="Buscar por nombre o código..."
                    value={busqueda}
                    onChange={(e) => setBusqueda(e.target.value)}
                />

                <button type="submit">Buscar</button>
            </form>

            {error && (
                <p role="alert" className="drivers-page__error">
                    {error}
                </p>
            )}

            {mensaje && (
                <p role="status" className="drivers-page__success">
                    {mensaje}
                </p>
            )}

            <DriversTable
                conductores={conductores}
                puedeGestionar={puedeGestionar}
                cargando={cargando}
                onEditar={abrirFormulario}
                onEliminar={eliminarConductor}
                onAsignar={abrirAsignacion}
            />

            {!cargando && conductores.length > 0 && (
                <div className="drivers-page__pagination">
                    <button
                        disabled={pagina <= 1}
                        onClick={() => setPagina((actual) => actual - 1)}
                    >
                        Anterior
                    </button>

                    <span>
                        Página {pagina} de {totalPaginas}
                    </span>

                    <button
                        disabled={pagina >= totalPaginas}
                        onClick={() => setPagina((actual) => actual + 1)}
                    >
                        Siguiente
                    </button>
                </div>
            )}

            {mostrarFormulario && (
                <div className="drivers-page__modal">
                    <DriverForm
                        conductor={conductorSeleccionado}
                        guardando={guardando}
                        onGuardar={guardarConductor}
                        onCancelar={cerrarFormulario}
                    />
                </div>
            )}

            {conductorAsignacion && (
                <div className="drivers-page__modal">
                    <DriverAssignmentForm
                        conductor={conductorAsignacion}
                        guardando={guardandoAsignacion}
                        onAsignar={gestionarAsignacion}
                        onDesvincular={gestionarDesvinculacion}
                        onCancelar={() => {
                            if (!guardandoAsignacion) {
                                setConductorAsignacion(null);
                            }
                        }}
                    />
                </div>
            )}
        </section>
    );
}

export default DriversPage;
