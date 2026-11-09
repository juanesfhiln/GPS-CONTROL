import { useCallback, useEffect, useState } from "react";

import "leaflet/dist/leaflet.css";
import "react-leaflet-cluster/dist/assets/MarkerCluster.css";
import "react-leaflet-cluster/dist/assets/MarkerCluster.Default.css";

import VehicleMap from "../features/map/components/VehicleMap";
import { getVehicles } from "../features/vehicles/services/vehicleService";
import type { Vehicle } from "../features/vehicles/types/vehicle";
import "../features/map/styles/map.scss";

function MapPage() {
    const [vehiculos, setVehiculos] = useState<Vehicle[]>([]);
    const [cargando, setCargando] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const cargarVehiculos = useCallback(async () => {
        try {
        const respuesta = await getVehicles(1, 100);
        setVehiculos(respuesta.resultados);
        setError(null);
        } catch (err) {
        setError(
            err instanceof Error
            ? err.message
            : "No fue posible cargar los vehículos."
        );
        } finally {
        setCargando(false);
        }
    }, []);

    useEffect(() => {
        cargarVehiculos();

        const intervalo = window.setInterval(() => {
        if (document.visibilityState === "visible") {
            cargarVehiculos();
        }
        }, 15000);

        return () => window.clearInterval(intervalo);
    }, [cargarVehiculos]);

    const vehiculosConUbicacion = vehiculos.filter(
        (vehiculo) =>
        vehiculo.latitude !== null &&
        vehiculo.longitude !== null
    ).length;

    if (cargando) {
        return (
        <main className="map-page">
            <div className="map-page__message">
            Cargando información del mapa...
            </div>
        </main>
        );
    }

    return (
        <main className="map-page">
        <header className="map-page__header">
            <div>
            <h1>Mapa de vehículos</h1>
            <p>
                Visualización y seguimiento de la flota en tiempo real.
            </p>
            </div>

            <button
            type="button"
            className="map-page__refresh"
            onClick={cargarVehiculos}
            >
            Actualizar
            </button>
        </header>

        <section className="map-page__statistics">
            <article className="map-page__stat">
            <span>Total de vehículos</span>
            <strong>{vehiculos.length}</strong>
            </article>

            <article className="map-page__stat">
            <span>Con ubicación</span>
            <strong>{vehiculosConUbicacion}</strong>
            </article>

            <article className="map-page__stat">
            <span>Sin ubicación</span>
            <strong>{vehiculos.length - vehiculosConUbicacion}</strong>
            </article>
        </section>

        {error && (
            <div className="map-page__error" role="alert">
            {error}
            </div>
        )}

        {vehiculosConUbicacion > 0 ? (
            <section className="map-page__container">
            <VehicleMap vehiculos={vehiculos} />
            </section>
        ) : (
            <div className="map-page__empty">
            No hay vehículos con coordenadas disponibles.
            </div>
        )}
        </main>
    );
}

export default MapPage;
