import { useEffect, useState, type FormEvent } from "react";
import { getVehicles } from "../../vehicles/services/vehicleService";
import type { Vehicle } from "../../vehicles/types/vehicle";
import type { Passenger } from "../types/passenger";

interface PassengerAssignmentFormProps {
    passenger: Passenger;
    guardando: boolean;
    onAssign: (passengerId: number, unitId: number) => Promise<void>;
    onUnassign: (passengerId: number, unitId: number) => Promise<void>;
    onCancel: () => void;
}

function PassengerAssignmentForm({
    passenger,
    guardando,
    onAssign,
    onUnassign,
    onCancel
}: PassengerAssignmentFormProps) {
    const [vehicles, setVehicles] = useState<Vehicle[]>([]);
    const [unitId, setUnitId] = useState("");
    const [cargando, setCargando] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        async function cargarVehiculos() {
            try {
                const respuesta = await getVehicles(1, 100);
                setVehicles(respuesta.resultados);
            } catch (error) {
                setError(
                    error instanceof Error
                        ? error.message
                        : "No fue posible cargar los vehículos."
                );
            } finally {
                setCargando(false);
            }
        }

        cargarVehiculos();
    }, []);

    async function manejarAsignacion(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();

        if (!unitId) {
            setError("Selecciona un vehículo.");
            return;
        }

        setError("");

        try {
            await onAssign(passenger.id, Number(unitId));
        } catch (error) {
            setError(
                error instanceof Error
                    ? error.message
                    : "No fue posible asignar el pasajero."
            );
        }
    }

    async function manejarDesasignacion() {
        if (passenger.assigned_unit_id === null) return;

        setError("");

        try {
            await onUnassign(passenger.id, passenger.assigned_unit_id);
        } catch (error) {
            setError(
                error instanceof Error
                    ? error.message
                    : "No fue posible desasignar el pasajero."
            );
        }
    }

    return (
        <section className="passenger-assignment">
            <h2>Asignación de pasajero</h2>

            <p>
                Pasajero: <strong>{passenger.name}</strong>
            </p>

            {passenger.assigned_unit_id !== null ? (
                <>
                    <p>
                        Vehículo actual: {passenger.assigned_unit_id}
                    </p>

                    <button
                        type="button"
                        onClick={manejarDesasignacion}
                        disabled={guardando}
                    >
                        {guardando ? "Procesando..." : "Desasignar vehículo"}
                    </button>
                </>
            ) : (
                <form onSubmit={manejarAsignacion}>
                    <label htmlFor="passenger-vehicle">
                        Seleccionar vehículo
                    </label>

                    {cargando ? (
                        <p>Cargando vehículos...</p>
                    ) : (
                        <select
                            id="passenger-vehicle"
                            value={unitId}
                            onChange={event => setUnitId(event.target.value)}
                            required
                        >
                            <option value="">Selecciona un vehículo</option>

                            {vehicles.map(vehicle => (
                                <option key={vehicle.id} value={vehicle.id}>
                                    {vehicle.name} (ID: {vehicle.id})
                                </option>
                            ))}
                        </select>
                    )}

                    <button
                        type="submit"
                        disabled={cargando || guardando || vehicles.length === 0}
                    >
                        {guardando ? "Asignando..." : "Asignar pasajero"}
                    </button>
                </form>
            )}

            {error && <p className="form-error">{error}</p>}

            <button type="button" onClick={onCancel} disabled={guardando}>
                Cerrar
            </button>
        </section>
    );
}


export default PassengerAssignmentForm;