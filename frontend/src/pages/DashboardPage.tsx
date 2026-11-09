
import { useEffect, useRef, useState } from "react";
import {
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

import {
  obtenerResumenDashboard,
  type DashboardSummary,
} from "../features/dashboard/services/dashboardService";

import "../features/dashboard/styles/dashboard.scss";

const COLORES_ESTADOS = ["#159b78", "#89919b", "#d94b4b"];
const COLORES_CONDUCTORES = ["#159b78", "#d94b4b"];

function DashboardPage() {
  const [resumen, setResumen] = useState<DashboardSummary | null>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [ultimaConsultaExitosa, setUltimaConsultaExitosa] =
    useState<Date | null>(null);

  const peticionEnCurso = useRef(false);

  useEffect(() => {
    let activo = true;

    async function cargarResumen() {
      if (
        !activo ||
        document.visibilityState !== "visible" ||
        peticionEnCurso.current
      ) {
        return;
      }

      peticionEnCurso.current = true;

      try {
        const datos = await obtenerResumenDashboard();

        if (activo) {
          setResumen(datos);
          setError("");
          setUltimaConsultaExitosa(new Date());
        }
      } catch (err) {
        if (activo) {
          setError(
            err instanceof Error
              ? err.message
              : "No se pudo actualizar el dashboard."
          );
        }
      } finally {
        peticionEnCurso.current = false;

        if (activo) {
          setCargando(false);
        }
      }
    }

    function manejarVisibilidad() {
      if (document.visibilityState === "visible") {
        void cargarResumen();
      }
    }

    void cargarResumen();

    const intervalo = window.setInterval(() => {
      void cargarResumen();
    }, 15000);

    document.addEventListener("visibilitychange", manejarVisibilidad);

    return () => {
      activo = false;
      window.clearInterval(intervalo);
      document.removeEventListener("visibilitychange", manejarVisibilidad);
    };
  }, []);

  if (cargando) {
    return (
      <section
        className="dashboard"
        aria-busy="true"
        aria-label="Cargando dashboard"
      >
        <header className="dashboard__header">
          <div>
            <span className="dashboard__eyebrow">
              Centro de monitoreo
            </span>

            <h1 className="dashboard__title">
              Dashboard GPS Control
            </h1>

            <div className="dashboard__connection">
              <span className="dashboard__connection-dot dashboard__connection-dot--loading" />
              <strong>Consultando información...</strong>
            </div>

            <p className="dashboard__subtitle">
              Estamos obteniendo los datos de la flota vehicular.
            </p>
          </div>
        </header>

        <section aria-label="Indicadores generales">
          <h2 className="dashboard__section-title">
            Indicadores generales
          </h2>

          <div className="dashboard__grid">
            {Array.from({ length: 10 }).map((_, index) => (
              <article
                className="dashboard__card dashboard__card--skeleton"
                key={index}
              >
                <span className="dashboard__skeleton dashboard__skeleton--label" />
                <span className="dashboard__skeleton dashboard__skeleton--value" />
              </article>
            ))}
          </div>
        </section>

        <footer className="dashboard__footer">
          <span className="dashboard__skeleton dashboard__skeleton--footer" />
        </footer>
      </section>
    );
  }

  if (error && !resumen) {
    return (
      <section className="dashboard">
        <header className="dashboard__header">
          <div>
            <h1 className="dashboard__title">
              Dashboard GPS Control
            </h1>

            <div className="dashboard__connection">
              <span className="dashboard__connection-dot dashboard__connection-dot--offline" />
              <strong>Conexión perdida</strong>
            </div>
          </div>
        </header>

        <p className="dashboard__error" role="alert">
          {error}
        </p>
      </section>
    );
  }

  if (!resumen) {
    return (
      <section className="dashboard">
        <p>No hay información disponible.</p>
      </section>
    );
  }

  const indicadores = [
    {
      titulo: "Total de vehículos",
      valor: resumen.total_vehiculos,
      clase: "primary",
    },
    {
      titulo: "Total de conductores",
      valor: resumen.total_conductores,
      clase: "primary",
    },
    {
      titulo: "Total de pasajeros",
      valor: resumen.total_pasajeros,
      clase: "primary",
    },
    {
      titulo: "Vehículos con conductor",
      valor: resumen.vehiculos_con_conductor,
      clase: "moving",
    },
    {
      titulo: "Vehículos sin conductor",
      valor: resumen.vehiculos_sin_conductor,
      clase: "offline",
    },
    {
      titulo: "En movimiento",
      valor: resumen.en_movimiento,
      clase: "moving",
    },
    {
      titulo: "Detenidos",
      valor: resumen.detenidos,
      clase: "stopped",
    },
    {
      titulo: "Sin señal",
      valor: resumen.sin_senal,
      clase: "offline",
    },
    {
      titulo: "Con ubicación disponible",
      valor: resumen.vehiculos_con_ubicacion,
      clase: "location",
    },
    {
      titulo: "Velocidad promedio",
      valor: `${resumen.velocidad_promedio} km/h`,
      clase: "speed",
    },
  ];

  const datosEstados = [
    {
      nombre: "En movimiento",
      valor: resumen.distribucion_estados.en_movimiento,
    },
    {
      nombre: "Detenidos",
      valor: resumen.distribucion_estados.detenidos,
    },
    {
      nombre: "Sin señal",
      valor: resumen.distribucion_estados.sin_senal,
    },
  ];

  const datosConductores = [
    {
      nombre: "Con conductor",
      valor: resumen.distribucion_conductores.con_conductor,
    },
    {
      nombre: "Sin conductor",
      valor: resumen.distribucion_conductores.sin_conductor,
    },
  ];

  return (
    <section className="dashboard">
      <header className="dashboard__header">
        <div>
          <span className="dashboard__eyebrow">
            Centro de monitoreo
          </span>

          <h1 className="dashboard__title">
            Dashboard GPS Control
          </h1>

          <div className="dashboard__connection">
            <span
              className={`dashboard__connection-dot ${
                error ? "dashboard__connection-dot--offline" : ""
              }`}
            />

            <strong>
              {error ? "Conexión perdida" : "Conectado"}
            </strong>

            <span className="dashboard__connection-time">
              Última consulta exitosa:{" "}
              {ultimaConsultaExitosa
                ? ultimaConsultaExitosa.toLocaleTimeString("es-CO")
                : "Pendiente"}
            </span>
          </div>

          {error && (
            <p className="dashboard__warning" role="alert">
              No se pudo actualizar la información. Se muestran los últimos
              datos disponibles.
            </p>
          )}

          <p className="dashboard__subtitle">
            Resumen del estado actual de la flota vehicular.
          </p>
        </div>
      </header>

      <section aria-label="Indicadores generales">
        <h2 className="dashboard__section-title">
          Indicadores generales
        </h2>

        <div className="dashboard__grid">
          {indicadores.map((indicador) => (
            <article
              className={`dashboard__card dashboard__card--${indicador.clase}`}
              key={indicador.titulo}
            >
              <p className="dashboard__card-label">
                {indicador.titulo}
              </p>

              <p className="dashboard__card-value">
                {indicador.valor}
              </p>
            </article>
          ))}
        </div>
      </section>

      <section className="dashboard__charts">
        <h2 className="dashboard__section-title">
          Análisis de la flota
        </h2>

        <div className="dashboard__charts-grid">
          <article className="dashboard__chart-card">
            <h3 className="dashboard__chart-title">
              Estado de los vehículos
            </h3>

            <p className="dashboard__chart-description">
              Distribución de los vehículos según su estado actual.
            </p>

            <div
              className="dashboard__chart"
              role="img"
              aria-label={`Estados: ${datosEstados.map((dato) => `${dato.nombre}: ${dato.valor}`).join(", ")}`}
            >
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={datosEstados}
                    dataKey="valor"
                    nameKey="nombre"
                    cx="50%"
                    cy="45%"
                    outerRadius="75%"
                    paddingAngle={2}
                  >
                    {datosEstados.map((dato, index) => (
                      <Cell
                        key={dato.nombre}
                        fill={COLORES_ESTADOS[index]}
                      />
                    ))}
                  </Pie>

                  <Tooltip />
                  <Legend verticalAlign="bottom" />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </article>

          <article className="dashboard__chart-card">
            <h3 className="dashboard__chart-title">
              Asignación de conductores
            </h3>

            <p className="dashboard__chart-description">
              Vehículos con conductor asignado y sin asignación.
            </p>

            <div
              className="dashboard__chart"
              role="img"
              aria-label={`Asignaciones: ${datosConductores.map((dato) => `${dato.nombre}: ${dato.valor}`).join(", ")}`}
            >
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={datosConductores}
                    dataKey="valor"
                    nameKey="nombre"
                    cx="50%"
                    cy="45%"
                    outerRadius="75%"
                    paddingAngle={2}
                  >
                    {datosConductores.map((dato, index) => (
                      <Cell
                        key={dato.nombre}
                        fill={COLORES_CONDUCTORES[index]}
                      />
                    ))}
                  </Pie>

                  <Tooltip />
                  <Legend verticalAlign="bottom" />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </article>
        </div>
      </section>

      <footer className="dashboard__footer">
        <strong>Última actualización:</strong>{" "}
        {resumen.ultima_actualizacion
          ? new Date(resumen.ultima_actualizacion).toLocaleString("es-CO")
          : "Sin información disponible"}
      </footer>
    </section>
  );
}

export default DashboardPage;
