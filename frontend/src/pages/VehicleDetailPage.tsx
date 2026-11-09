import { useEffect, useState } from "react";
import { useParams } from "react-router";

import { useAuth } from "../features/auth/context/AuthContext";

import {
    getVehicles,
    getVehicleCustomFields,
    createVehicleCustomField,
    updateVehicleCustomField,
    deleteVehicleCustomField
} from "../features/vehicles/services/vehicleService";

import type { Vehicle } from "../features/vehicles/types/vehicle";

import { getDrivers } from "../features/drivers/services/driverService";
import type { Driver } from "../features/drivers/types/driver";

import { getPassengers } from "../features/passengers/services/passengerService";
import type { Passenger } from "../features/passengers/types/passenger";

import type { VehicleCustomField } from "../features/vehicles/services/vehicleService";

import "../features/vehicles/styles/vehicle-detail.scss";

interface CustomFieldDraft {
    nombre: string;
    valor: string;
}

function VehicleDetailPage() {
    const { id } = useParams<{ id: string }>();
    const { usuario } = useAuth();

    const [vehiculo, setVehiculo] = useState<Vehicle | null>(null);
    const [cargando, setCargando] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const [conductorAsignado, setConductorAsignado] =
        useState<Driver | null>(null);

    const [pasajerosAsignados, setPasajerosAsignados] =
        useState<Passenger[]>([]);

    const [errorPasajeros, setErrorPasajeros] =
        useState<string | null>(null);

    const [camposPersonalizados, setCamposPersonalizados] =
        useState<VehicleCustomField[]>([]);

    const [camposEditados, setCamposEditados] =
        useState<Record<string, CustomFieldDraft>>({});

    const [campoGuardando, setCampoGuardando] =
        useState<string | null>(null);

    const [campoCreando, setCampoCreando] = useState(false);

    const [campoEliminando, setCampoEliminando] =
        useState<number | null>(null);

    const [campoPendienteEliminar, setCampoPendienteEliminar] =
        useState<number | null>(null);

    const [nuevoCampo, setNuevoCampo] = useState({
        nombre: "",
        valor: ""
    });

    const [mensajeCampos, setMensajeCampos] =
        useState<string | null>(null);

    const [errorCampos, setErrorCampos] =
        useState<string | null>(null);

    const puedeEditar =
        usuario?.rol === "Administrador" ||
        usuario?.rol === "Operador";

    // Cargar información del vehículo
    useEffect(() => {
        let activo = true;

        async function cargarVehiculo() {
            try {
                setCargando(true);
                setError(null);

                const respuesta = await getVehicles(1, 100);

                const encontrado = respuesta.resultados.find(
                    (item) => item.id === Number(id)
                );

                if (!encontrado) {
                    if (activo) {
                        setError("No se encontró el vehículo solicitado.");
                    }
                    return;
                }

                const [respuestaConductores, respuestaPasajeros] =
                    await Promise.all([
                        getDrivers(1, 100),
                        getPassengers(1, 100).catch(() => null)
                    ]);

                if (!activo) return;

                const conductor = respuestaConductores.resultados.find(
                    (item) => item.assigned_unit_id === encontrado.id
                );

                const asignados = respuestaPasajeros
                    ? respuestaPasajeros.resultados.filter(
                        (pasajero) =>
                            pasajero.assigned_unit_id === encontrado.id
                    )
                    : [];

                setVehiculo(encontrado);
                setConductorAsignado(conductor ?? null);
                setPasajerosAsignados(asignados);

                setErrorPasajeros(
                    respuestaPasajeros
                        ? null
                        : "No fue posible cargar los pasajeros asignados."
                );

                try {
                    const campos = await getVehicleCustomFields(encontrado.id);

                    if (!activo) return;

                    setCamposPersonalizados(campos);
                    setCamposEditados({});
                    setErrorCampos(null);
                } catch {
                    if (!activo) return;

                    setCamposPersonalizados([]);
                    setErrorCampos(
                        "No fue posible consultar los campos personalizados."
                    );
                }
            } catch {
                if (activo) {
                    setError(
                        "No fue posible cargar la información del vehículo."
                    );
                }
            } finally {
                if (activo) {
                    setCargando(false);
                }
            }
        }

        cargarVehiculo();

        return () => {
            activo = false;
        };
    }, [id]);

    // Actualizar borradores de campos
    function cambiarCampo(
        campoId: string,
        propiedad: keyof CustomFieldDraft,
        valor: string
    ) {
        const campo = camposPersonalizados.find(
            (item) => String(item.id) === campoId
        );

        if (!campo) return;

        setCamposEditados((actuales) => ({
            ...actuales,
            [campoId]: {
                ...(actuales[campoId] ?? {
                    nombre: campo.nombre,
                    valor: campo.valor
                }),
                [propiedad]: valor
            }
        }));

        setMensajeCampos(null);
        setErrorCampos(null);
    }

    // Actualizar un campo personalizado
    async function guardarCampo(campoId: string) {
        if (!vehiculo || !puedeEditar) return;

        const campoIdNumerico = Number(campoId);

        const campoOriginal = camposPersonalizados.find(
            (item) => item.id === campoIdNumerico
        );

        if (!campoOriginal) {
            setErrorCampos(
                "No se encontró el campo que deseas actualizar."
            );
            return;
        }

        const borrador = camposEditados[campoId] ?? {
            nombre: campoOriginal.nombre,
            valor: campoOriginal.valor
        };

        if (
            !Number.isInteger(campoIdNumerico) ||
            campoIdNumerico <= 0 ||
            !borrador.nombre.trim()
        ) {
            setErrorCampos("Los datos del campo no son válidos.");
            return;
        }

        try {
            setCampoGuardando(campoId);
            setMensajeCampos(null);
            setErrorCampos(null);

            await updateVehicleCustomField(
                vehiculo.id,
                campoIdNumerico,
                borrador.nombre.trim(),
                borrador.valor
            );

            setCamposPersonalizados((actuales) =>
                actuales.map((campo) =>
                    campo.id === campoIdNumerico
                        ? {
                              ...campo,
                              nombre: borrador.nombre.trim(),
                              valor: borrador.valor
                          }
                        : campo
                )
            );

            setCamposEditados((actuales) => {
                const copia = { ...actuales };
                delete copia[campoId];
                return copia;
            });

            setMensajeCampos(
                "Campo personalizado actualizado correctamente."
            );
        } catch (error) {
            setErrorCampos(
                error instanceof Error
                    ? error.message
                    : "No fue posible actualizar el campo."
            );
        } finally {
            setCampoGuardando(null);
        }
    }

    // Crear un campo personalizado
    async function crearCampo() {
        if (!vehiculo || !puedeEditar) return;

        const nombre = nuevoCampo.nombre.trim();

        if (!nombre) {
            setErrorCampos("El nombre del campo es obligatorio.");
            return;
        }

        try {
            setCampoCreando(true);
            setMensajeCampos(null);
            setErrorCampos(null);

            await createVehicleCustomField(
                vehiculo.id,
                nombre,
                nuevoCampo.valor
            );

            const campos = await getVehicleCustomFields(vehiculo.id);

            setCamposPersonalizados(campos);
            setCamposEditados({});

            setNuevoCampo({
                nombre: "",
                valor: ""
            });

            setMensajeCampos(
                "Campo personalizado creado correctamente."
            );
        } catch (error) {
            setErrorCampos(
                error instanceof Error
                    ? error.message
                    : "No fue posible crear el campo personalizado."
            );
        } finally {
            setCampoCreando(false);
        }
    }

    // Eliminar un campo personalizado
    async function eliminarCampo(campoId: number) {
        if (!vehiculo || !puedeEditar) return;

        try {
            setCampoEliminando(campoId);
            setMensajeCampos(null);
            setErrorCampos(null);

            await deleteVehicleCustomField(vehiculo.id, campoId);

            const campos = await getVehicleCustomFields(vehiculo.id);

            setCamposPersonalizados(campos);

            setCamposEditados((actuales) => {
                const copia = { ...actuales };
                delete copia[String(campoId)];
                return copia;
            });

            setMensajeCampos(
                "Campo personalizado eliminado correctamente."
            );

            setCampoPendienteEliminar(null);
        } catch (error) {
            setErrorCampos(
                error instanceof Error
                    ? error.message
                    : "No fue posible eliminar el campo personalizado."
            );
        } finally {
            setCampoEliminando(null);
        }
    }

    // Cancelar eliminación
    function cancelarEliminacion() {
        if (campoEliminando !== null) return;

        setCampoPendienteEliminar(null);
        setErrorCampos(null);
    }

    if (cargando) {
        return (
            <main className="vehicle-detail">
                Cargando vehículo...
            </main>
        );
    }

    if (error || !vehiculo) {
        return (
            <main className="vehicle-detail">
                <p>{error || "Vehículo no encontrado."}</p>
            </main>
        );
    }

    const campoSeleccionado = camposPersonalizados.find(
        (campo) => campo.id === campoPendienteEliminar
    );

    return (
        <main className="vehicle-detail">
            <header className="vehicle-detail__header">
                <div>
                    <h1>{vehiculo.name}</h1>
                    <p>Detalle del vehículo #{vehiculo.id}</p>
                </div>
            </header>

            {/* Información general */}
            <section className="vehicle-detail__section">
                <h2>Información general</h2>

                <div className="vehicle-detail__grid">
                    <article>
                        <span>Identificador</span>
                        <strong>{vehiculo.id}</strong>
                    </article>

                    <article>
                        <span>Estado</span>
                        <strong>
                            {vehiculo.status.replace("_", " ")}
                        </strong>
                    </article>
                    <article>
                        <span>Comunicación</span>
                        <strong>
                            {vehiculo.communication_status.replaceAll("_", " ")}
                        </strong>
                    </article>

                    <article>
                        <span>Estado GPS</span>
                        <strong>
                            {vehiculo.position_status.replaceAll("_", " ")}
                        </strong>
                    </article>
                    <article>
                        <span>Velocidad</span>
                        <strong>{vehiculo.speed} km/h</strong>
                    </article>

                    <article>
                        <span>Rumbo</span>
                        <strong>
                            {vehiculo.heading_cardinal || "Sin información"}
                        </strong>
                    </article>

                    <article>
                        <span>Latitud</span>
                        <strong>
                            {vehiculo.latitude ?? "Sin información"}
                        </strong>
                    </article>

                    <article>
                        <span>Longitud</span>
                        <strong>
                            {vehiculo.longitude ?? "Sin información"}
                        </strong>
                    </article>

                    <article>
                        <span>Altitud</span>
                        <strong>
                            {vehiculo.altitude !== null
                                ? `${vehiculo.altitude} m`
                                : "Sin información"}
                        </strong>
                    </article>

                    <article>
                        <span>Último mensaje</span>
                        <strong>
                            {vehiculo.last_message_time
                                ? new Date(
                                      vehiculo.last_message_time
                                  ).toLocaleString("es-CO")
                                : "Sin información"}
                        </strong>
                    </article>
                </div>
            </section>

            {/* Campos personalizados */}
            <section className="vehicle-detail__section">
                <h2>Campos personalizados</h2>

                {mensajeCampos && (
                    <p className="vehicle-detail__success">
                        {mensajeCampos}
                    </p>
                )}

                {errorCampos && campoPendienteEliminar === null && (
                    <p className="vehicle-detail__error">
                        {errorCampos}
                    </p>
                )}

                {/* Formulario de creación */}
                {puedeEditar && (
                    <div className="vehicle-detail__custom-field">
                        <h3>Agregar campo personalizado</h3>

                        <label>
                            Nombre
                            <input
                                type="text"
                                value={nuevoCampo.nombre}
                                maxLength={100}
                                placeholder="Nombre del campo"
                                onChange={(event) =>
                                    setNuevoCampo((actual) => ({
                                        ...actual,
                                        nombre: event.target.value
                                    }))
                                }
                            />
                        </label>

                        <label>
                            Valor
                            <input
                                type="text"
                                value={nuevoCampo.valor}
                                placeholder="Valor del campo"
                                onChange={(event) =>
                                    setNuevoCampo((actual) => ({
                                        ...actual,
                                        valor: event.target.value
                                    }))
                                }
                            />
                        </label>

                        <button
                            type="button"
                            onClick={crearCampo}
                            disabled={campoCreando}
                        >
                            {campoCreando
                                ? "Creando..."
                                : "Agregar campo"}
                        </button>
                    </div>
                )}

                {/* Listado de campos */}
                {camposPersonalizados.length > 0 ? (
                    <div className="vehicle-detail__custom-fields">
                        {camposPersonalizados.map((campo) => {
                            const campoId = String(campo.id);

                            const borrador = camposEditados[campoId] ?? {
                                nombre: campo.nombre,
                                valor: campo.valor
                            };

                            return (
                                <article
                                    className="vehicle-detail__custom-field"
                                    key={campo.id}
                                >
                                    <span>Campo #{campo.id}</span>

                                    {puedeEditar ? (
                                        <>
                                            <label>
                                                Nombre
                                                <input
                                                    type="text"
                                                    value={borrador.nombre}
                                                    maxLength={100}
                                                    onChange={(event) =>
                                                        cambiarCampo(
                                                            campoId,
                                                            "nombre",
                                                            event.target.value
                                                        )
                                                    }
                                                />
                                            </label>

                                            <label>
                                                Valor
                                                <input
                                                    type="text"
                                                    value={borrador.valor}
                                                    onChange={(event) =>
                                                        cambiarCampo(
                                                            campoId,
                                                            "valor",
                                                            event.target.value
                                                        )
                                                    }
                                                />
                                            </label>

                                            <button
                                                type="button"
                                                onClick={() =>
                                                    guardarCampo(campoId)
                                                }
                                                disabled={
                                                    campoGuardando !== null ||
                                                    campoEliminando !== null
                                                }
                                            >
                                                {campoGuardando === campoId
                                                    ? "Guardando..."
                                                    : "Guardar cambios"}
                                            </button>

                                            <button
                                                type="button"
                                                className="vehicle-detail__delete-button"
                                                onClick={() => {
                                                    setErrorCampos(null);
                                                    setCampoPendienteEliminar(
                                                        campo.id
                                                    );
                                                }}
                                                disabled={
                                                    campoEliminando !== null ||
                                                    campoGuardando !== null
                                                }
                                            >
                                                Eliminar
                                            </button>
                                        </>
                                    ) : (
                                        <>
                                            <span>Nombre</span>
                                            <strong>
                                                {campo.nombre || "Sin nombre"}
                                            </strong>

                                            <span>Valor</span>
                                            <strong>
                                                {campo.valor || "Sin valor"}
                                            </strong>
                                        </>
                                    )}
                                </article>
                            );
                        })}
                    </div>
                ) : (
                    !errorCampos && (
                        <p>
                            Este vehículo no tiene campos personalizados
                            registrados.
                        </p>
                    )
                )}
            </section>

            {/* Conductor asignado */}
            <section className="vehicle-detail__section">
                <h2>Conductor asignado</h2>

                {conductorAsignado ? (
                    <div className="vehicle-detail__grid">
                        <article>
                            <span>Nombre</span>
                            <strong>{conductorAsignado.name}</strong>
                        </article>

                        <article>
                            <span>ID</span>
                            <strong>{conductorAsignado.id}</strong>
                        </article>

                        <article>
                            <span>Código</span>
                            <strong>
                                {conductorAsignado.code || "Sin información"}
                            </strong>
                        </article>

                        <article>
                            <span>Teléfono</span>
                            <strong>
                                {conductorAsignado.phone || "Sin información"}
                            </strong>
                        </article>
                    </div>
                ) : (
                    <p>
                        No hay un conductor asignado a este vehículo.
                    </p>
                )}
            </section>

            {/* Pasajeros asignados */}
            <section className="vehicle-detail__section">
                <h2>Pasajeros asignados</h2>

                {errorPasajeros ? (
                    <p>{errorPasajeros}</p>
                ) : pasajerosAsignados.length > 0 ? (
                    <div className="vehicle-detail__grid">
                        {pasajerosAsignados.map((pasajero) => (
                            <article key={pasajero.id}>
                                <span>Nombre</span>
                                <strong>{pasajero.name}</strong>

                                <span>Identificador</span>
                                <strong>{pasajero.id}</strong>

                                <span>Código</span>
                                <strong>
                                    {pasajero.code || "Sin información"}
                                </strong>

                                <span>Teléfono</span>
                                <strong>
                                    {pasajero.phone || "Sin información"}
                                </strong>

                                <span>Asignación</span>
                                <strong>Asignado</strong>
                            </article>
                        ))}
                    </div>
                ) : (
                    <p>
                        No hay pasajeros asignados a este vehículo.
                    </p>
                )}
            </section>

            {/* Modal de confirmación de eliminación */}
            {campoPendienteEliminar !== null && (
                <div
                    className="vehicle-detail__modal-overlay"
                    onClick={(event) => {
                        if (event.target === event.currentTarget) {
                            cancelarEliminacion();
                        }
                    }}
                >
                    <div
                        className="vehicle-detail__modal"
                        role="dialog"
                        aria-modal="true"
                        aria-labelledby="delete-modal-title"
                        aria-describedby="delete-modal-description"
                    >
                        <h2 id="delete-modal-title">
                            Confirmar eliminación
                        </h2>

                        <p id="delete-modal-description">
                            ¿Estás seguro de que deseas eliminar el campo
                            personalizado{" "}
                            <strong>
                                {campoSeleccionado?.nombre ||
                                    `#${campoPendienteEliminar}`}
                            </strong>
                            ?
                        </p>

                        <p>
                            Esta acción eliminará el campo del vehículo
                            y no se puede deshacer.
                        </p>

                        {errorCampos && (
                            <p className="vehicle-detail__modal-error">
                                {errorCampos}
                            </p>
                        )}

                        <div className="vehicle-detail__modal-actions">
                            <button
                                type="button"
                                className="vehicle-detail__modal-cancel"
                                onClick={cancelarEliminacion}
                                disabled={campoEliminando !== null}
                            >
                                Cancelar
                            </button>

                            <button
                                type="button"
                                className="vehicle-detail__modal-confirm"
                                onClick={() =>
                                    eliminarCampo(campoPendienteEliminar)
                                }
                                disabled={campoEliminando !== null}
                            >
                                {campoEliminando === campoPendienteEliminar
                                    ? "Eliminando..."
                                    : "Sí, eliminar"}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </main>
    );
}

export default VehicleDetailPage;