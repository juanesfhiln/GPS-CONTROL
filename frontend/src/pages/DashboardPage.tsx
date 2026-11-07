
import { useEffect, useRef, useState } from "react";

import {
  obtenerResumenDashboard,
  type DashboardSummary,
} from "../features/dashboard/services/dashboardService";

import "../features/dashboard/styles/dashboard.scss";

function DashboardPage() {
  const [resumen, setResumen] = useState<DashboardSummary | null>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const peticionEnCurso = useRef(false);
  const [ultimaConsultaExitosa, setUltimaConsultaExitosa] = useState<Date | null>(null);


  useEffect(() => {

    let activo = true;

    async function cargarResumen() {
      // Evitar solicitudes simultáneas.
      if (peticionEnCurso.current) return;

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

    void cargarResumen();

    const intervalo = window.setInterval(() => {
      void cargarResumen();
    }, 15000);

    return () => {
      activo = false;
      window.clearInterval(intervalo);
    };
  }, []);


  if (cargando) {
    return (
      <section className="dashboard" aria-busy="true" aria-label="Cargando dashboard">
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
            {Array.from({ length: 6 }).map((_, index) => (
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
              <span className="dashboard__connection-time">
                Última consulta exitosa: Sin información
              </span>
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

          <p className="dashboard__subtitle">
            Resumen del estado actual de la flota vehicular.
          </p>
        </div>
      </header>

      <section aria-label="Indicadores de vehículos">
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
