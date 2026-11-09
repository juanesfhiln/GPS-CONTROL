import { useEffect, useState, type SyntheticEvent } from "react";

import { useAuth } from "../features/auth/context/AuthContext";

import PassengersTable from "../features/passengers/components/PassengersTable";
import PassengerForm from "../features/passengers/components/PassengerForm";
import PassengerAssignmentForm from "../features/passengers/components/PassengerAssignmentForm";

import {
    getPassengers,
    createPassenger,
    updatePassenger,
    deletePassenger,
    assignPassenger,
    unassignPassenger
} from "../features/passengers/services/passengerService";

import type {
    Passenger,
    PassengerPayload
} from "../features/passengers/types/passenger";

import "../features/passengers/styles/passengers.scss";

function PassengersPage() {
    const { usuario } = useAuth();

    const [pasajeros, setPasajeros] = useState<Passenger[]>([]);
    const [pagina, setPagina] = useState(1);
    const [totalPaginas, setTotalPaginas] = useState(1);
    const [busqueda, setBusqueda] = useState("");
    const [filtro, setFiltro] = useState("");

    const [cargando, setCargando] = useState(true);
    const [guardando, setGuardando] = useState(false);
    const [guardandoAsignacion, setGuardandoAsignacion] = useState(false);
    const [pasajeroAEliminar, setPasajeroAEliminar] = useState<Passenger | null>(null);

    const [error, setError] = useState("");
    const [mensaje, setMensaje] = useState("");

    const [mostrarFormulario, setMostrarFormulario] = useState(false);
    const [pasajeroSeleccionado, setPasajeroSeleccionado] = useState<Passenger | null>(null);

    const [pasajeroAsignacion, setPasajeroAsignacion] = useState<Passenger | null>(null);

    const puedeGestionar =
        usuario?.rol === "Admin" ||
        usuario?.rol === "Administrador" ||
        usuario?.rol === "Operador";

    async function cargarPasajeros() {
        try {
            setCargando(true);
            setError("");

            const respuesta = await getPassengers(pagina, 10, filtro);

            setPasajeros(respuesta.resultados);
            setTotalPaginas(respuesta.total_paginas);
        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : "No fue posible cargar los pasajeros."
            );
        } finally {
            setCargando(false);
        }
    }

    useEffect(() => {
        void cargarPasajeros();
    }, [pagina, filtro]);

    function abrirFormulario(pasajero: Passenger | null = null) {
        setPasajeroSeleccionado(pasajero);
        setMostrarFormulario(true);
        setError("");
        setMensaje("");
    }

    function cerrarFormulario() {
        if (guardando) return;

        setMostrarFormulario(false);
        setPasajeroSeleccionado(null);
    }

    function abrirAsignacion(pasajero: Passenger) {
        setPasajeroAsignacion(pasajero);
        setError("");
        setMensaje("");
    }

    async function guardarPasajero(datos: PassengerPayload) {
        try {
            setGuardando(true);
            setError("");
            setMensaje("");

            if (pasajeroSeleccionado) {
                await updatePassenger(pasajeroSeleccionado.id, datos);
                setMensaje("Pasajero actualizado correctamente.");
            } else {
                await createPassenger(datos);
                setMensaje("Pasajero registrado correctamente.");
            }

            setMostrarFormulario(false);
            setPasajeroSeleccionado(null);

            await cargarPasajeros();
        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : "No fue posible guardar el pasajero."
            );
        } finally {
            setGuardando(false);
        }
    }

    async function gestionarAsignacion(
        passengerId: number,
        unitId: number
    ) {
        try {
            setGuardandoAsignacion(true);
            setError("");
            setMensaje("");

            await assignPassenger(passengerId, unitId);

            setPasajeros(actuales =>
                actuales.map(pasajero =>
                    pasajero.id === passengerId
                        ? { ...pasajero, assigned_unit_id: unitId }
                        : pasajero
                )
            );

            setPasajeroAsignacion(null);
            setMensaje("Pasajero asignado correctamente.");
        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : "No fue posible asignar el pasajero."
            );
        } finally {
            setGuardandoAsignacion(false);
        }
    }

    async function gestionarDesasignacion(
        passengerId: number,
        unitId: number
    ) {
        try {
            setGuardandoAsignacion(true);
            setError("");
            setMensaje("");

            await unassignPassenger(passengerId, unitId);

            setPasajeros(actuales =>
                actuales.map(pasajero =>
                    pasajero.id === passengerId
                        ? { ...pasajero, assigned_unit_id: null }
                        : pasajero
                )
            );

            setPasajeroAsignacion(null);
            setMensaje("Pasajero desasignado correctamente.");
        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : "No fue posible desasignar el pasajero."
            );
        } finally {
            setGuardandoAsignacion(false);
        }
    }

    async function eliminarPasajero(pasajero: Passenger) {
        try {
            setError("");
            setMensaje("");

            await deletePassenger(pasajero.id);

            setMensaje("Pasajero eliminado correctamente.");
            setPasajeroAEliminar(null);

            await cargarPasajeros();
        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : "No fue posible eliminar el pasajero."
            );
        }
    }

    function buscarPasajeros(evento: SyntheticEvent<HTMLFormElement>) {
        evento.preventDefault();
        setPagina(1);
        setFiltro(busqueda.trim());
    }

    return (
        <section className="passengers-page">
            <header className="passengers-page__header">
                <div>
                    <h1>Gestión de pasajeros</h1>
                    <p>
                        Consulta y administra los pasajeros registrados en Wialon.
                    </p>
                </div>

                {puedeGestionar && (
                    <button type="button" onClick={() => abrirFormulario()}>
                        Nuevo pasajero
                    </button>
                )}
            </header>

            <form
                className="passengers-page__search"
                onSubmit={buscarPasajeros}
            >
                <input
                    type="search"
                    placeholder="Buscar por nombre o código..."
                    value={busqueda}
                    onChange={evento => setBusqueda(evento.target.value)}
                />

                <button type="submit">Buscar</button>
            </form>

            {error && (
                <p role="alert" className="passengers-page__error">
                    {error}
                </p>
            )}

            {mensaje && (
                <p role="status" className="passengers-page__success">
                    {mensaje}
                </p>
            )}

            <PassengersTable
                passengers={pasajeros}
                puedeAdministrar={puedeGestionar}
                onEdit={abrirFormulario}
                onDelete={setPasajeroAEliminar}
                onAssign={abrirAsignacion}
            />

            {!cargando && pasajeros.length > 0 && (
                <div className="passengers-page__pagination">
                    <button
                        type="button"
                        disabled={pagina <= 1}
                        onClick={() => setPagina(actual => actual - 1)}
                    >
                        Anterior
                    </button>

                    <span>
                        Página {pagina} de {totalPaginas}
                    </span>

                    <button
                        type="button"
                        disabled={pagina >= totalPaginas}
                        onClick={() => setPagina(actual => actual + 1)}
                    >
                        Siguiente
                    </button>
                </div>
            )}

            {mostrarFormulario && (
                <div className="passengers-page__modal">
                    <PassengerForm
                        passenger={pasajeroSeleccionado}
                        guardando={guardando}
                        onSubmit={guardarPasajero}
                        onCancel={cerrarFormulario}
                    />
                </div>
            )}

            {pasajeroAsignacion && (
                <div className="passengers-page__modal">
                    <PassengerAssignmentForm
                        passenger={pasajeroAsignacion}
                        guardando={guardandoAsignacion}
                        onAssign={gestionarAsignacion}
                        onUnassign={gestionarDesasignacion}
                        onCancel={() => {
                            if (!guardandoAsignacion) {
                                setPasajeroAsignacion(null);
                            }
                        }}
                    />
                </div>
            )}

            {pasajeroAEliminar && (
                <div className="passengers-page__modal">
                    <div className="passenger-confirm">
                        <h2>Confirmar eliminación</h2>

                        <p>
                            ¿Estás seguro de eliminar al pasajero{" "}
                            <strong>{pasajeroAEliminar.name}</strong>?
                        </p>

                        <div className="passenger-confirm__actions">
                            <button
                                type="button"
                                onClick={() => setPasajeroAEliminar(null)}
                            >
                                Cancelar
                            </button>

                            <button
                                type="button"
                                className="passenger-confirm__delete"
                                onClick={() => eliminarPasajero(pasajeroAEliminar)}
                            >
                                Eliminar pasajero
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </section>
    );
}

export default PassengersPage;
