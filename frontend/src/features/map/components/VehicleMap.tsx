
import { useEffect, useMemo } from "react";
import { useNavigate } from "react-router";
import {
    MapContainer,
    Marker,
    Popup,
    TileLayer,
    useMap,
} from "react-leaflet";
import MarkerClusterGroup from "react-leaflet-cluster";
import L from "leaflet";
import type { Vehicle } from "../../vehicles/types/vehicle";

interface VehicleMapProps {
    vehiculos: Vehicle[];
}

const iconosVehiculos = {
    en_movimiento: new L.DivIcon({
        className: "vehicle-marker",
        html: '<div class="vehicle-marker__dot vehicle-marker__dot--moving"></div>',
        iconSize: [20, 20],
        iconAnchor: [10, 10],
    }),
    detenido: new L.DivIcon({
        className: "vehicle-marker",
        html: '<div class="vehicle-marker__dot vehicle-marker__dot--stopped"></div>',
        iconSize: [20, 20],
        iconAnchor: [10, 10],
    }),
    "sin_señal": new L.DivIcon({
        className: "vehicle-marker",
        html: '<div class="vehicle-marker__dot vehicle-marker__dot--offline"></div>',
        iconSize: [20, 20],
        iconAnchor: [10, 10],
    }),
};

const iconoPredeterminado = iconosVehiculos["sin_señal"];

function AjustarVista({ vehiculos }: VehicleMapProps) {
    const mapa = useMap();

    useEffect(() => {
        const coordenadas = vehiculos
            .filter(
                (vehiculo) =>
                    vehiculo.latitude !== null &&
                    vehiculo.longitude !== null &&
                    Number.isFinite(vehiculo.latitude) &&
                    Number.isFinite(vehiculo.longitude)
            )
            .map(
                (vehiculo) =>
                    [
                        vehiculo.latitude!,
                        vehiculo.longitude!,
                    ] as L.LatLngTuple
            );

        if (coordenadas.length === 0) {
            mapa.setView([4.711, -74.0721], 6);
            return;
        }

        if (coordenadas.length === 1) {
            mapa.setView(coordenadas[0], 14);
            return;
        }

        mapa.fitBounds(L.latLngBounds(coordenadas), {
            padding: [40, 40],
            maxZoom: 14,
        });
    }, [vehiculos, mapa]);

    return null;
}

function VehicleMap({ vehiculos }: VehicleMapProps) {
    const navigate = useNavigate();

    const vehiculosConUbicacion = useMemo(
        () =>
            vehiculos.filter(
                (vehiculo) =>
                    vehiculo.latitude !== null &&
                    vehiculo.longitude !== null &&
                    Number.isFinite(vehiculo.latitude) &&
                    Number.isFinite(vehiculo.longitude)
            ),
        [vehiculos]
    );

    return (
        <MapContainer
            center={[4.711, -74.0721]}
            zoom={6}
            scrollWheelZoom
            className="vehicle-map"
        >
            <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            <AjustarVista vehiculos={vehiculosConUbicacion} />

            <MarkerClusterGroup
                chunkedLoading
                iconCreateFunction={(cluster: { getChildCount: () => number }) => {
                    const cantidad = cluster.getChildCount();

                    const nivel =
                        cantidad <= 10
                            ? "small"
                            : cantidad <= 20
                                ? "medium"
                                : "large";

                    return L.divIcon({
                        html: `<div><span>${cantidad}</span></div>`,
                        className: `marker-cluster marker-cluster-${nivel}`,
                        iconSize: L.point(40, 40),
                    });
                }}
            >
                {vehiculosConUbicacion.map((vehiculo) => {
                    const icono =
                        iconosVehiculos[
                            vehiculo.status as keyof typeof iconosVehiculos
                        ] ?? iconoPredeterminado;

                    return (
                        <Marker
                            key={vehiculo.id}
                            position={[
                                vehiculo.latitude!,
                                vehiculo.longitude!,
                            ]}
                            icon={icono}
                        >
                            <Popup>
                                <div className="vehicle-map__popup">
                                    <strong>{vehiculo.name}</strong>

                                    <p>ID: {vehiculo.id}</p>

                                    <p>
                                        Estado: {vehiculo.status.replace("_", " ")}
                                    </p>

                                    <p>
                                        Velocidad: {vehiculo.speed} km/h
                                    </p>

                                    <p>
                                        Rumbo: {vehiculo.heading_cardinal || "Sin información"}
                                    </p>

                                    <p>
                                        Último mensaje:{" "}
                                        {vehiculo.last_message_time
                                            ? new Date(
                                                vehiculo.last_message_time
                                            ).toLocaleString("es-CO")
                                            : "Sin información"}
                                    </p>
                                </div>

                                <button
                                    type="button"
                                    className="vehicle-map__detail-button"
                                    onClick={() =>
                                        navigate(`/vehiculos/${vehiculo.id}`)
                                    }
                                >
                                    Ver detalle
                                </button>
                            </Popup>
                        </Marker>
                    );
                })}
            </MarkerClusterGroup>
        </MapContainer>
    );
}

export default VehicleMap;
