
import { useEffect, useState, type SyntheticEvent } from "react";
import { getTripHistory } from "../features/trips/services/tripService";
import { getVehicles } from "../features/vehicles/services/vehicleService";
import type { TripHistoryResponse } from "../features/trips/types/trip";
import type { Vehicle } from "../features/vehicles/types/vehicle";
import "../features/trips/styles/trips.scss";

export default function TripsPage() {
    const [vehiculos, setVehiculos] = useState<Vehicle[]>([]);
    const [vehiculoId, setVehiculoId] = useState("");
    const [fechaInicio, setFechaInicio] = useState("");
    const [fechaFin, setFechaFin] = useState("");
    const [historial, setHistorial] = useState<TripHistoryResponse | null>(null);
    const [cargando, setCargando] = useState(false);
    const [cargandoVehiculos, setCargandoVehiculos] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        let activo = true;

        async function cargarVehiculos() {
            try {
                const respuesta = await getVehicles(1, 100);

                if (activo) {
                    setVehiculos(respuesta.resultados);
                }
            } catch {
                if (activo) {
                    setError("No fue posible cargar los vehículos.");
                }
            } finally {
                if (activo) {
                    setCargandoVehiculos(false);
                }
            }
        }

        cargarVehiculos();

        return () => {
            activo = false;
        };
    }, []);

    async function consultarHistorial(evento: SyntheticEvent<HTMLFormElement>) {
        evento.preventDefault();

        if (!vehiculoId || !fechaInicio || !fechaFin) {
            setError("Selecciona un vehículo y ambas fechas.");
            return;
        }

        if (new Date(fechaInicio) >= new Date(fechaFin)) {
            setError("La fecha inicial debe ser anterior a la fecha final.");
            return;
        }

        setCargando(true);
        setError("");
        setHistorial(null);

        try {
            const resultado = await getTripHistory(
                Number(vehiculoId),
                new Date(fechaInicio).toISOString(),
                new Date(fechaFin).toISOString()
            );

            setHistorial(resultado);
        } catch (error) {
            setError(
                error instanceof Error
                    ? error.message
                    : "No fue posible consultar el historial."
            );
        } finally {
            setCargando(false);
        }
    }

    function formatearFecha(fecha: string) {
        return new Date(fecha).toLocaleString("es-CO", {
            dateStyle: "short",
            timeStyle: "short"
        });
    }

    function formatearDuracion(segundos: number) {
        const horas = Math.floor(segundos / 3600);
        const minutos = Math.floor((segundos % 3600) / 60);

        return `${horas} h ${minutos} min`;
    }

    return (
        <main className="trips-page">
            <header className="trips-page__header">
                <div>
                    <h1>Historial de viajes</h1>
                    <p>Consulta los recorridos registrados por vehículo.</p>
                </div>
            </header>

            <form className="trips-page__filters" onSubmit={consultarHistorial}>
                <div className="trips-page__field">
                    <label htmlFor="vehiculo">Vehículo</label>
                    <select
                        id="vehiculo"
                        value={vehiculoId}
                        onChange={(evento) => setVehiculoId(evento.target.value)}
                        disabled={cargandoVehiculos}
                    >
                        <option value="">Seleccionar vehículo</option>
                        {vehiculos.map((vehiculo) => (
                            <option key={vehiculo.id} value={vehiculo.id}>
                                {vehiculo.name} ({vehiculo.id})
                            </option>
                        ))}
                    </select>
                </div>

                <div className="trips-page__field">
                    <label htmlFor="fechaInicio">Fecha inicial</label>
                    <input
                        id="fechaInicio"
                        type="datetime-local"
                        value={fechaInicio}
                        onChange={(evento) => setFechaInicio(evento.target.value)}
                    />
                </div>

                <div className="trips-page__field">
                    <label htmlFor="fechaFin">Fecha final</label>
                    <input
                        id="fechaFin"
                        type="datetime-local"
                        value={fechaFin}
                        onChange={(evento) => setFechaFin(evento.target.value)}
                    />
                </div>

                <button type="submit" disabled={cargando || cargandoVehiculos}>
                    {cargando ? "Consultando..." : "Consultar historial"}
                </button>
            </form>

            {error && (
                <div className="trips-page__message trips-page__message--error">
                    {error}
                </div>
            )}

            {historial && (
                <section className="trips-page__results">
                    {historial.simulated && (
                        <div className="trips-page__message trips-page__message--warning">
                            Datos simulados: no representan recorridos GPS reales.
                        </div>
                    )}

                    <div className="trips-page__summary">
                        <div>
                            <span>Vehículo</span>
                            <strong>{historial.vehicle_name}</strong>
                        </div>
                        <div>
                            <span>Total de viajes</span>
                            <strong>{historial.total_viajes}</strong>
                        </div>
                        <div>
                            <span>Periodo consultado</span>
                            <strong>
                                {formatearFecha(historial.fecha_inicio)} -{" "}
                                {formatearFecha(historial.fecha_fin)}
                            </strong>
                        </div>
                    </div>

                    {historial.viajes.length > 0 ? (
                        <div className="trips-page__table-container">
                            <table className="trips-page__table">
                                <thead>
                                    <tr>
                                        <th>Inicio</th>
                                        <th>Finalización</th>
                                        <th>Duración</th>
                                        <th>Distancia</th>
                                        <th>Vel. promedio</th>
                                        <th>Vel. máxima</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {historial.viajes.map((viaje) => (
                                        <tr key={viaje.id}>
                                            <td>{formatearFecha(viaje.start_time)}</td>
                                            <td>{formatearFecha(viaje.end_time)}</td>
                                            <td>{formatearDuracion(viaje.duration_seconds)}</td>
                                            <td>{viaje.distance_km.toFixed(2)} km</td>
                                            <td>{viaje.average_speed.toFixed(1)} km/h</td>
                                            <td>{viaje.max_speed.toFixed(1)} km/h</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    ) : (
                        <p>No se encontraron viajes en el periodo seleccionado.</p>
                    )}
                </section>
            )}
        </main>
    );
}
