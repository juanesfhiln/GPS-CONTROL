
import { useEffect, useState } from "react";
import { useParams } from "react-router";

import { useAuth } from "../features/auth/context/AuthContext";

import {
    getVehicles,
    updateVehicleCustomField
} from "../features/vehicles/services/vehicleService";

import type {
    Vehicle,
    VehicleCustomField
} from "../features/vehicles/types/vehicle";

import { getDrivers } from "../features/drivers/services/driverService";
import type { Driver } from "../features/drivers/types/driver";

import { getPassengers } from "../features/passengers/services/passengerService";
import type { Passenger } from "../features/passengers/types/passenger";

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

    const [conductorAsignado, setConductorAsignado] = useState<Driver | null>(null);
    const [pasajerosAsignados, setPasajerosAsignados] = useState<Passenger[]>([]);
    const [errorPasajeros, setErrorPasajeros] = useState<string | null>(null);

    const [camposEditados, setCamposEditados] = useState<Record<string, CustomFieldDraft>>({});
    const [campoGuardando, setCampoGuardando] = useState<string | null>(null);
    const [mensajeCampos, setMensajeCampos] = useState<string | null>(null);
    const [errorCampos, setErrorCampos] = useState<string | null>(null);

    const puedeEditar = usuario?.rol === "Administrador" || usuario?.rol === "Operador";

    useEffect(() => {
        async function cargarVehiculo() {
            try {
                const respuesta = await getVehicles(1, 100);

                const encontrado = respuesta.resultados.find(
                    (item) => item.id === Number(id)
                );

                if (!encontrado) {
                    setError("No se encontró el vehículo solicitado.");
                    return;
                }

                const respuestaConductores = await getDrivers(1, 100);

                const conductor = respuestaConductores.resultados.find(
                    (item) => item.assigned_unit_id === encontrado.id
                );

                try {
                    const respuestaPasajeros = await getPassengers(1, 100);

                    const asignados = respuestaPasajeros.resultados.filter(
                        (pasajero) => pasajero.assigned_unit_id === encontrado.id
                    );

                    setPasajerosAsignados(asignados);
                    setErrorPasajeros(null);
                } catch {
                    setPasajerosAsignados([]);
                    setErrorPasajeros("No fue posible cargar los pasajeros asignados.");
                }

                setConductorAsignado(conductor ?? null);
                setVehiculo(encontrado);

                const borradores: Record<string, CustomFieldDraft> = {};

                Object.entries(encontrado.custom_fields ?? {}).forEach(
                    ([campoId, campo]) => {
                        borradores[campoId] = {
                            nombre: campo.n ?? "",
                            valor: campo.v ?? ""
                        };
                    }
                );

                setCamposEditados(borradores);

            } catch {
                setError("No fue posible cargar la información del vehículo.");
            } finally {
                setCargando(false);
            }
        }

        cargarVehiculo();
    }, [id]);

    function cambiarCampo(
        campoId: string,
        propiedad: keyof CustomFieldDraft,
        valor: string
    ) {
        setCamposEditados((actuales) => ({
            ...actuales,
            [campoId]: {
                ...actuales[campoId],
                [propiedad]: valor
            }
        }));

        setMensajeCampos(null);
        setErrorCampos(null);
    }

    async function guardarCampo(campoId: string) {
        if (!vehiculo || !puedeEditar) {
            return;
        }

        const borrador = camposEditados[campoId];
        const campoIdNumerico = Number(campoId);

        if (
            !borrador ||
            !Number.isInteger(campoIdNumerico) ||
            campoIdNumerico <= 0
        ) {
            setErrorCampos("Los datos del campo no son válidos.");
            return;
        }

        if (!borrador.nombre.trim()) {
            setErrorCampos("El nombre del campo no puede estar vacío.");
            return;
        }

        try {
            setCampoGuardando(campoId);
            setMensajeCampos(null);
            setErrorCampos(null);

            await updateVehicleCustomField(
                vehiculo.id,
                campoIdNumerico,
                borrador.nombre,
                borrador.valor
            );

            setVehiculo((actual) => {
                if (!actual) {
                    return actual;
                }

                const camposActualizados: Record<string, VehicleCustomField> = {
                    ...actual.custom_fields,
                    [campoId]: {
                        ...actual.custom_fields[campoId],
                        n: borrador.nombre,
                        v: borrador.valor
                    }
                };

                return {
                    ...actual,
                    custom_fields: camposActualizados
                };
            });

            setMensajeCampos("Campo personalizado actualizado correctamente.");

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

    if (cargando) {
        return <main className="vehicle-detail">Cargando vehículo...</main>;
    }

    if (error || !vehiculo) {
        return (
            <main className="vehicle-detail">
                <p>{error || "Vehículo no encontrado."}</p>
            </main>
        );
    }

    return (
        <main className="vehicle-detail">
            <header className="vehicle-detail__header">
                <div>
                    <h1>{vehiculo.name}</h1>
                    <p>Detalle del vehículo #{vehiculo.id}</p>
                </div>
            </header>

            <section className="vehicle-detail__section">
                <h2>Información general</h2>

                <div className="vehicle-detail__grid">
                    <article>
                        <span>Identificador</span>
                        <strong>{vehiculo.id}</strong>
                    </article>

                    <article>
                        <span>Estado</span>
                        <strong>{vehiculo.status.replace("_", " ")}</strong>
                    </article>

                    <article>
                        <span>Velocidad</span>
                        <strong>{vehiculo.speed} km/h</strong>
                    </article>

                    <article>
                        <span>Rumbo</span>
                        <strong>{vehiculo.heading_cardinal || "Sin información"}</strong>
                    </article>

                    <article>
                        <span>Latitud</span>
                        <strong>{vehiculo.latitude ?? "Sin información"}</strong>
                    </article>

                    <article>
                        <span>Longitud</span>
                        <strong>{vehiculo.longitude ?? "Sin información"}</strong>
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

            <section className="vehicle-detail__section">
                <h2>Campos personalizados</h2>

                {Object.keys(vehiculo.custom_fields ?? {}).length > 0 ? (
                    <>
                        <div className="vehicle-detail__custom-fields">
                            {Object.entries(vehiculo.custom_fields).map(
                                ([campoId, campo]) => {
                                    const borrador = camposEditados[campoId] ?? {
                                        nombre: campo.n ?? "",
                                        valor: campo.v ?? ""
                                    };

                                    return (
                                        <article
                                            className="vehicle-detail__custom-field"
                                            key={campoId}
                                        >
                                            <span>Campo #{campoId}</span>

                                            {puedeEditar ? (
                                                <>
                                                    <label>
                                                        Nombre
                                                        <input
                                                            type="text"
                                                            value={borrador.nombre}
                                                            onChange={(event) =>
                                                                cambiarCampo(
                                                                    campoId,
                                                                    "nombre",
                                                                    event.target.value
                                                                )
                                                            }
                                                            maxLength={100}
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
                                                        onClick={() => guardarCampo(campoId)}
                                                        disabled={campoGuardando !== null}
                                                    >
                                                        {campoGuardando === campoId
                                                            ? "Guardando..."
                                                            : "Guardar cambios"}
                                                    </button>
                                                </>
                                            ) : (
                                                <>
                                                    <span>Nombre</span>
                                                    <strong>{campo.n || "Sin nombre"}</strong>

                                                    <span>Valor</span>
                                                    <strong>{campo.v || "Sin valor"}</strong>
                                                </>
                                            )}
                                        </article>
                                    );
                                }
                            )}
                        </div>

                        {mensajeCampos && (
                            <p className="vehicle-detail__success">
                                {mensajeCampos}
                            </p>
                        )}

                        {errorCampos && (
                            <p className="vehicle-detail__error">
                                {errorCampos}
                            </p>
                        )}
                    </>
                ) : (
                    <p>Este vehículo no tiene campos personalizados registrados.</p>
                )}
            </section>

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
                            <strong>{conductorAsignado.code || "Sin información"}</strong>
                        </article>

                        <article>
                            <span>Teléfono</span>
                            <strong>{conductorAsignado.phone || "Sin información"}</strong>
                        </article>
                    </div>
                ) : (
                    <p>No hay un conductor asignado a este vehículo.</p>
                )}
            </section>

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
                                <strong>{pasajero.code || "Sin información"}</strong>

                                <span>Teléfono</span>
                                <strong>{pasajero.phone || "Sin información"}</strong>

                                <span>Asignación</span>
                                <strong>Asignado</strong>
                            </article>
                        ))}
                    </div>
                ) : (
                    <p>No hay pasajeros asignados a este vehículo.</p>
                )}
            </section>
        </main>
    );
}

export default VehicleDetailPage;
