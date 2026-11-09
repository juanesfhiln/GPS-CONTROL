
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";

import { getVehicles } from "../features/vehicles/services/vehicleService";
import type { Vehicle } from "../features/vehicles/types/vehicle";
import { getAllVehiclesForExport } from "../features/vehicles/services/vehicleExportService";
import { exportVehiclesToCSV } from "../features/vehicles/services/vehicleCsvService";

import "../features/vehicles/styles/vehicles.scss";

function VehiclesPage() {
    const navigate = useNavigate();

    const [vehiculos, setVehiculos] = useState<Vehicle[]>([]);
    const [buscar, setBuscar] = useState("");
    const [estado, setEstado] = useState("todos");
    const [pagina, setPagina] = useState(1);
    const [totalPaginas, setTotalPaginas] = useState(1);
    const [total, setTotal] = useState(0);
    const [cargando, setCargando] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [exportando, setExportando] = useState(false);

    useEffect(() => {
        let activo = true;

        async function cargarVehiculos() {
            try {
                setCargando(true);
                setError(null);

                const respuesta = await getVehicles(pagina, 10, buscar, estado);

                if (!activo) return;

                setVehiculos(respuesta.resultados);
                setTotal(respuesta.total);
                setTotalPaginas(respuesta.total_paginas);
            } catch {
                if (activo) {
                    setError("No fue posible cargar los vehículos.");
                }
            } finally {
                if (activo) {
                    setCargando(false);
                }
            }
        }

        cargarVehiculos();

        return () => {
            activo = false;
        };
    }, [pagina, buscar, estado]);

    function cambiarBusqueda(valor: string) {
        setBuscar(valor);
        setPagina(1);
    }

    async function exportarVehiculos() {
        try {
            setExportando(true);
            setError(null);

            const vehiculosExportar = await getAllVehiclesForExport(
                buscar,
                estado
            );

            exportVehiclesToCSV(vehiculosExportar);
        } catch (error) {
            setError(
                error instanceof Error
                    ? error.message
                    : "No fue posible exportar los vehículos."
            );
        } finally {
            setExportando(false);
        }
    }

    return (
        <main className="vehicles-page">
            <header className="vehicles-page__header">
                <div>
                    <h1>Vehículos</h1>
                    <p>Consulta y administra la información de la flota.</p>
                </div>

                <span className="vehicles-page__total">
                    {total} vehículos
                </span>
            </header>

            <section className="vehicles-page__filters">
                <input
                    type="search"
                    placeholder="Buscar por nombre, placa o identificador..."
                    value={buscar}
                    onChange={(event) => cambiarBusqueda(event.target.value)}
                />

                <select
                    value={estado}
                    onChange={(event) => setEstado(event.target.value)}
                >
                    <option value="todos">Todos los estados</option>
                    <option value="en_movimiento">En movimiento</option>
                    <option value="detenido">Detenidos</option>
                    <option value="sin_señal">Sin señal</option>

                </select>

                <button type="button" onClick={exportarVehiculos} disabled={cargando || exportando}>
                    {exportando ? "Exportando..." : "Exportar CSV"}
                </button>
                    
            </section>

            {error && (
                <p className="vehicles-page__error">{error}</p>
            )}

            {cargando ? (
                <p>Cargando vehículos...</p>
            ) : vehiculos.length > 0 ? (
                <>
                    <div className="vehicles-page__table-container">
                        <table className="vehicles-page__table">
                            <thead>
                                <tr>
                                    <th>Identificador</th>
                                    <th>Vehículo</th>
                                    <th>Movimiento</th>
                                    <th>Comunicación</th>
                                    <th>Estado GPS</th>
                                    <th>Velocidad</th>
                                    <th>Último mensaje</th>
                                    <th>Acciones</th>
                                </tr>
                            </thead>

                            <tbody>
                                {vehiculos.map((vehiculo) => (
                                    <tr key={vehiculo.id}>
                                        <td>{vehiculo.id}</td>
                                        <td>{vehiculo.name}</td>
                                        <td>
                                            {vehiculo.status.replaceAll("_", " ")}
                                        </td>
                                        <td>
                                            {vehiculo.communication_status.replaceAll("_", " ")}
                                        </td>
                                        <td>
                                            {vehiculo.position_status.replaceAll("_", " ")}
                                        </td>
                                        <td>{vehiculo.speed} km/h</td>
                                        <td>
                                            {vehiculo.last_message_time
                                                ? new Date(vehiculo.last_message_time).toLocaleString("es-CO")
                                                : "Sin información"}
                                        </td>
                                        <td>
                                            <button type="button" onClick={() => navigate(`/vehiculos/${vehiculo.id}`)}>
                                                Ver detalle
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    <footer className="vehicles-page__pagination">
                        <button type="button" disabled={pagina <= 1} onClick={() => setPagina((actual) => actual - 1)}>
                            Anterior
                        </button>

                        <span>
                            Página {pagina} de {totalPaginas}
                        </span>

                        <button
                            type="button"
                            disabled={pagina >= totalPaginas}
                            onClick={() => setPagina((actual) => actual + 1)}
                        >
                            Siguiente
                        </button>
                    </footer>
                </>
            ) : (
                <p className="vehicles-page__empty">
                    No se encontraron vehículos.
                </p>
            )}
        </main>
    );
}

export default VehiclesPage;
