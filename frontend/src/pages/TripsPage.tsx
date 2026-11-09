import {
    useEffect,
    useMemo,
    useState,
    type SyntheticEvent
} from "react";

import {
    CircleMarker,
    MapContainer,
    Polyline,
    TileLayer,
    Tooltip,
    useMap
} from "react-leaflet";

import L from "leaflet";

import { Play, Pause, RotateCcw } from "lucide-react";

import { getTripHistory } from "../features/trips/services/tripService";
import { getVehicles } from "../features/vehicles/services/vehicleService";

import type {
    Trip,
    TripHistoryResponse,
    TripRoutePoint
} from "../features/trips/types/trip";

import type { Vehicle } from "../features/vehicles/types/vehicle";

import "../features/trips/styles/trips.scss";


interface RouteMapProps {
    puntos: TripRoutePoint[];
    indiceActual: number;
}


function AjustarMapa({ puntos }: RouteMapProps) {
    const mapa = useMap();

    useEffect(() => {
        if (puntos.length === 0) return;

        const coordenadas = puntos.map(
            (punto) =>
                [punto.latitude, punto.longitude] as L.LatLngTuple
        );

        mapa.fitBounds(L.latLngBounds(coordenadas), {
            padding: [40, 40],
            maxZoom: 15
        });
    }, [puntos, mapa]);

    return null;
}


function RouteMap({ puntos, indiceActual }: RouteMapProps) {
    const posiciones = useMemo(
        () =>
            puntos.map(
                (punto) =>
                    [punto.latitude, punto.longitude] as L.LatLngTuple
            ),
        [puntos]
    );

    const puntoActual = puntos[indiceActual];

    return (
        <MapContainer
            center={[4.711, -74.0721]}
            zoom={13}
            scrollWheelZoom
            className="trips-page__map"
        >
            <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            <AjustarMapa
                puntos={puntos}
                indiceActual={indiceActual}
            />

            {posiciones.length > 1 && (
                <>
                    <Polyline
                        positions={posiciones}
                        pathOptions={{
                            color: "#1E8C93",
                            weight: 5,
                            opacity: 0.85
                        }}
                    />

                    {indiceActual > 0 && (
                        <Polyline
                            positions={posiciones.slice(0, indiceActual + 1)}
                            pathOptions={{
                                color: "#EB162C",
                                weight: 6,
                                opacity: 1
                            }}
                        />
                    )}
                </>
            )}

            {puntos.length > 0 && (
                <>
                    <CircleMarker
                        center={posiciones[0]}
                        radius={7}
                        pathOptions={{
                            color: "#ffffff",
                            weight: 2,
                            fillColor: "#1E8C93",
                            fillOpacity: 1
                        }}
                    >
                        <Tooltip permanent direction="top">
                            Inicio
                        </Tooltip>
                    </CircleMarker>

                    <CircleMarker
                        center={posiciones[posiciones.length - 1]}
                        radius={7}
                        pathOptions={{
                            color: "#ffffff",
                            weight: 2,
                            fillColor: "#c62828",
                            fillOpacity: 1
                        }}
                    >
                        <Tooltip permanent direction="top">
                            Fin
                        </Tooltip>
                    </CircleMarker>
                </>
            )}

            {puntoActual && (
                <CircleMarker
                    center={[
                        puntoActual.latitude,
                        puntoActual.longitude
                    ]}
                    radius={9}
                    pathOptions={{
                        color: "#ffffff",
                        weight: 3,
                        fillColor: "#EB162C",
                        fillOpacity: 1
                    }}
                >
                    <Tooltip permanent direction="right">
                        Vehículo: {puntoActual.speed.toFixed(1)} km/h
                    </Tooltip>
                </CircleMarker>
            )}
        </MapContainer>
    );
}


export default function TripsPage() {
    const [vehiculos, setVehiculos] = useState<Vehicle[]>([]);
    const [vehiculoId, setVehiculoId] = useState("");
    const [fechaInicio, setFechaInicio] = useState("");
    const [fechaFin, setFechaFin] = useState("");

    const [historial, setHistorial] =
        useState<TripHistoryResponse | null>(null);

    const [viajeSeleccionado, setViajeSeleccionado] =
        useState<Trip | null>(null);

    const [indiceActual, setIndiceActual] = useState(0);
    const [reproduciendo, setReproduciendo] = useState(false);

    const [cargando, setCargando] = useState(false);
    const [cargandoVehiculos, setCargandoVehiculos] = useState(true);
    const [error, setError] = useState("");


    const puntosRuta = viajeSeleccionado?.route_points ?? [];

    const puntoActual = puntosRuta[indiceActual];


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


    useEffect(() => {
        if (!reproduciendo) return;

        if (indiceActual >= puntosRuta.length - 1) {
            setReproduciendo(false);
            return;
        }

        const temporizador = window.setTimeout(() => {
            setIndiceActual((actual) => actual + 1);
        }, 700);

        return () => window.clearTimeout(temporizador);
    }, [
        reproduciendo,
        indiceActual,
        puntosRuta.length
    ]);


    async function consultarHistorial(
        evento: SyntheticEvent<HTMLFormElement>
    ) {
        evento.preventDefault();

        if (!vehiculoId || !fechaInicio || !fechaFin) {
            setError("Selecciona un vehículo y ambas fechas.");
            return;
        }

        if (new Date(fechaInicio) >= new Date(fechaFin)) {
            setError(
                "La fecha inicial debe ser anterior a la fecha final."
            );
            return;
        }

        setCargando(true);
        setError("");
        setHistorial(null);
        setViajeSeleccionado(null);
        setReproduciendo(false);
        setIndiceActual(0);

        try {
            const resultado = await getTripHistory(
                Number(vehiculoId),
                new Date(fechaInicio).toISOString(),
                new Date(fechaFin).toISOString()
            );

            setHistorial(resultado);

            if (resultado.viajes.length > 0) {
                setViajeSeleccionado(resultado.viajes[0]);
                setIndiceActual(0);
            }
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


    function seleccionarViaje(viaje: Trip) {
        setReproduciendo(false);
        setIndiceActual(0);
        setViajeSeleccionado(viaje);
    }


    function reproducir() {
        if (puntosRuta.length < 2) return;

        if (indiceActual >= puntosRuta.length - 1) {
            setIndiceActual(0);
        }

        setReproduciendo(true);
    }


    function pausar() {
        setReproduciendo(false);
    }


    function reiniciar() {
        setReproduciendo(false);
        setIndiceActual(0);
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


    function formatearTiempo(segundos: number) {
        const minutos = Math.floor(segundos / 60);
        const segundosRestantes = segundos % 60;

        return `${String(minutos).padStart(2, "0")}:${String(
            segundosRestantes
        ).padStart(2, "0")}`;
    }


    return (
        <main className="trips-page">

            <header className="trips-page__header">
                <div>
                    <h1>Historial de viajes</h1>
                    <p>
                        Consulta y reproduce los recorridos de cada vehículo.
                    </p>
                </div>
            </header>


            <form
                className="trips-page__filters"
                onSubmit={consultarHistorial}
            >
                <div className="trips-page__field">
                    <label htmlFor="vehiculo">Vehículo</label>

                    <select
                        id="vehiculo"
                        value={vehiculoId}
                        onChange={(evento) =>
                            setVehiculoId(evento.target.value)
                        }
                        disabled={cargandoVehiculos}
                    >
                        <option value="">
                            Seleccionar vehículo
                        </option>

                        {vehiculos.map((vehiculo) => (
                            <option
                                key={vehiculo.id}
                                value={vehiculo.id}
                            >
                                {vehiculo.name} ({vehiculo.id})
                            </option>
                        ))}
                    </select>
                </div>


                <div className="trips-page__field">
                    <label htmlFor="fechaInicio">
                        Fecha inicial
                    </label>

                    <input
                        id="fechaInicio"
                        type="datetime-local"
                        value={fechaInicio}
                        onChange={(evento) =>
                            setFechaInicio(evento.target.value)
                        }
                    />
                </div>


                <div className="trips-page__field">
                    <label htmlFor="fechaFin">
                        Fecha final
                    </label>

                    <input
                        id="fechaFin"
                        type="datetime-local"
                        value={fechaFin}
                        onChange={(evento) =>
                            setFechaFin(evento.target.value)
                        }
                    />
                </div>


                <button
                    type="submit"
                    disabled={cargando || cargandoVehiculos}
                >
                    {cargando
                        ? "Consultando..."
                        : "Consultar historial"}
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
                            Datos simulados: los recorridos y velocidades
                            no representan registros GPS reales.
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
                                {formatearFecha(historial.fecha_inicio)}
                                {" - "}
                                {formatearFecha(historial.fecha_fin)}
                            </strong>
                        </div>
                    </div>


                    {historial.viajes.length > 0 ? (
                        <>
                            <section className="trips-page__route-section">
                                <div className="trips-page__section-header">
                                    <div>
                                        <h2>Visualización del recorrido</h2>
                                        <p>
                                            Selecciona un viaje para visualizar
                                            su ruta y reproducir su movimiento.
                                        </p>
                                    </div>
                                </div>


                                <div className="trips-page__trip-selector">
                                    {historial.viajes.map((viaje, indice) => (
                                        <button
                                            type="button"
                                            key={viaje.id}
                                            className={
                                                viajeSeleccionado?.id === viaje.id
                                                    ? "trips-page__trip-option trips-page__trip-option--active"
                                                    : "trips-page__trip-option"
                                            }
                                            onClick={() =>
                                                seleccionarViaje(viaje)
                                            }
                                        >
                                            <strong>
                                                Viaje {indice + 1}
                                            </strong>

                                            <span>
                                                {formatearFecha(viaje.start_time)}
                                            </span>

                                            <small>
                                                {viaje.distance_km.toFixed(2)} km
                                            </small>
                                        </button>
                                    ))}
                                </div>


                                {viajeSeleccionado && (
                                    <>
                                        <div className="trips-page__map-container">
                                            <RouteMap
                                                puntos={puntosRuta}
                                                indiceActual={indiceActual}
                                            />
                                        </div>


                                        <div className="trips-page__playback">
                                            <div className="trips-page__playback-info">
                                                <div>
                                                    <span>Velocidad actual</span>
                                                    <strong>
                                                        {puntoActual
                                                            ? puntoActual.speed.toFixed(1)
                                                            : "0.0"} km/h
                                                    </strong>
                                                </div>

                                                <div>
                                                    <span>Tiempo del recorrido</span>
                                                    <strong>
                                                        {puntoActual
                                                            ? formatearTiempo(
                                                                puntoActual.elapsed_seconds
                                                            )
                                                            : "00:00"}
                                                        {" / "}
                                                        {formatearTiempo(
                                                            viajeSeleccionado.duration_seconds
                                                        )}
                                                    </strong>
                                                </div>

                                                <div>
                                                    <span>Distancia</span>
                                                    <strong>
                                                        {viajeSeleccionado.distance_km.toFixed(2)}
                                                        {" km"}
                                                    </strong>
                                                </div>
                                            </div>


                                            <input
                                                className="trips-page__timeline"
                                                type="range"
                                                min={0}
                                                max={Math.max(
                                                    puntosRuta.length - 1,
                                                    0
                                                )}
                                                value={indiceActual}
                                                onChange={(evento) => {
                                                    setReproduciendo(false);
                                                    setIndiceActual(
                                                        Number(evento.target.value)
                                                    );
                                                }}
                                                disabled={puntosRuta.length < 2}
                                                aria-label="Posición de reproducción del recorrido"
                                            />


                                            <div className="trips-page__playback-controls">
                                                <button
                                                    type="button"
                                                    onClick={reproducir}
                                                    disabled={
                                                        reproduciendo ||
                                                        puntosRuta.length < 2
                                                    }
                                                >
                                                    <Play size={17} />
                                                    Reproducir
                                                </button>

                                                <button
                                                    type="button"
                                                    onClick={pausar}
                                                    disabled={!reproduciendo}
                                                >
                                                    <Pause size={17} />
                                                    Pausar
                                                </button>

                                                <button
                                                    type="button"
                                                    onClick={reiniciar}
                                                    disabled={puntosRuta.length < 2}
                                                >
                                                    <RotateCcw size={17} />
                                                    Reiniciar
                                                </button>
                                            </div>
                                        </div>
                                    </>
                                )}
                            </section>


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
                                            <tr
                                                key={viaje.id}
                                                className={
                                                    viajeSeleccionado?.id === viaje.id
                                                        ? "trips-page__table-row--selected"
                                                        : ""
                                                }
                                                onClick={() =>
                                                    seleccionarViaje(viaje)
                                                }
                                            >
                                                <td>
                                                    {formatearFecha(viaje.start_time)}
                                                </td>

                                                <td>
                                                    {formatearFecha(viaje.end_time)}
                                                </td>

                                                <td>
                                                    {formatearDuracion(
                                                        viaje.duration_seconds
                                                    )}
                                                </td>

                                                <td>
                                                    {viaje.distance_km.toFixed(2)} km
                                                </td>

                                                <td>
                                                    {viaje.average_speed.toFixed(1)} km/h
                                                </td>

                                                <td>
                                                    {viaje.max_speed.toFixed(1)} km/h
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </>
                    ) : (
                        <p>
                            No se encontraron viajes en el periodo seleccionado.
                        </p>
                    )}
                </section>
            )}
        </main>
    );
}