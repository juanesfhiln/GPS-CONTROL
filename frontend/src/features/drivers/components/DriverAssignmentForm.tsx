
import { useEffect, useState } from "react";

import type { Driver } from "../types/driver";
import type { Vehicle } from "../../vehicles/types/vehicle";

import { getVehicles } from "../../vehicles/services/vehicleService";
import { getDriverAssignments } from "../services/driverService";

interface DriverAssignmentFormProps {
    conductor: Driver;
    guardando: boolean;
    onAsignar: (driverId: number, unitId: number) => Promise<void>;
    onDesvincular: (driverId: number, unitId: number) => Promise<void>;
    onCancelar: () => void;
}

function DriverAssignmentForm({
    conductor,
    guardando,
    onAsignar,
    onDesvincular,
    onCancelar
}: DriverAssignmentFormProps) {
    const [vehiculos, setVehiculos] = useState<Vehicle[]>([]);
    const [vehiculoSeleccionado, setVehiculoSeleccionado] = useState("");
    const [cargando, setCargando] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        async function cargarVehiculos() {
            try {
                setCargando(true);
                setError("");

                const [respuestaVehiculos, respuestaAsignaciones] =
                    await Promise.all([
                        getVehicles(1, 100),
                        getDriverAssignments()
                    ]);

                if (!respuestaAsignaciones.completa) {
                    throw new Error(
                        "No fue posible verificar las asignaciones actuales."
                    );
                }

                const vehiculosOcupados = new Set(
                    respuestaAsignaciones.resultados.map(
                        (asignacion) => asignacion.unit_id
                    )
                );

                const disponibles = respuestaVehiculos.resultados.filter(
                    (vehiculo) => !vehiculosOcupados.has(vehiculo.id)
                );

                setVehiculos(disponibles);
            } catch (err) {
                setError(
                    err instanceof Error
                        ? err.message
                        : "No fue posible cargar los vehículos disponibles."
                );
            } finally {
                setCargando(false);
            }
        }
        void cargarVehiculos();
    }, []);

    async function asignar() {
        if (!vehiculoSeleccionado) {
            setError("Selecciona un vehículo.");
            return;
        }

        await onAsignar(
            conductor.id,
            Number(vehiculoSeleccionado)
        );
    }

    async function desvincular() {
        if (conductor.assigned_unit_id === null) return;

        await onDesvincular(
            conductor.id,
            conductor.assigned_unit_id
        );
    }

    return (
        <div className="driver-assignment">
            <h2>Asignación de conductor</h2>

            <p>
                Conductor: <strong>{conductor.name}</strong>
            </p>

            {error && <p role="alert">{error}</p>}

            {conductor.assigned_unit_id !== null ? (
                <>
                    <p>
                        Vehículo asignado:{" "}
                        <strong>{conductor.assigned_unit_id}</strong>
                    </p>

                    <button
                        type="button"
                        onClick={() => void desvincular()}
                        disabled={guardando}
                    >
                        {guardando ? "Procesando..." : "Desvincular vehículo"}
                    </button>
                </>
            ) : (
                <>
                    <label htmlFor="driver-vehicle">
                        Seleccionar vehículo
                    </label>

                    {cargando ? (
                        <p>Cargando vehículos...</p>
                    ) : (
                        <select
                            id="driver-vehicle"
                            value={vehiculoSeleccionado}
                            onChange={(e) => setVehiculoSeleccionado(e.target.value)}
                        >
                            <option value="">Selecciona un vehículo</option>

                            {vehiculos.map((vehiculo) => (
                                <option key={vehiculo.id} value={vehiculo.id}>
                                    {vehiculo.name} - ID: {vehiculo.id}
                                </option>
                            ))}
                        </select>
                    )}

                    <button
                        type="button"
                        onClick={() => void asignar()}
                        disabled={guardando || cargando || !vehiculoSeleccionado}
                    >
                        {guardando ? "Procesando..." : "Asignar vehículo"}
                    </button>
                </>
            )}

            <button
                type="button"
                onClick={onCancelar}
                disabled={guardando}
            >
                Cerrar
            </button>
        </div>
    );
}

export default DriverAssignmentForm;
