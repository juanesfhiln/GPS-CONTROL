
import { Link } from "react-router";

export default function LandingPage() {
  return (
    <main className="landing">
      <header className="landing__header">
        <h1>GPS Control</h1>

        <nav aria-label="Navegación principal">
          <Link to="/login">
            Iniciar sesión
          </Link>
        </nav>
      </header>

      <section className="landing__hero">
        <div>
          <p>MONITOREO INTELIGENTE DE FLOTAS</p>

          <h2>
            Controla tu flota.
            <br />
            Optimiza cada recorrido.
          </h2>

          <p>
            Supervisa vehículos en tiempo real,
            consulta sus recorridos y administra
            tu operación desde una sola plataforma.
          </p>

          <Link to="/login">
            Acceder a la plataforma
          </Link>
        </div>
      </section>

      <section className="landing__features">
        <h2>Todo el control de tu flota en un solo lugar</h2>

        <article>
          <h3>Monitoreo en tiempo real</h3>
          <p>
            Consulta la ubicación y el estado
            de tus vehículos.
          </p>
        </article>

        <article>
          <h3>Gestión de flotas</h3>
          <p>
            Administra vehículos, conductores
            y pasajeros.
          </p>
        </article>

        <article>
          <h3>Historial de recorridos</h3>
          <p>
            Consulta los desplazamientos
            y movimientos registrados.
          </p>
        </article>
      </section>

      <footer className="landing__footer">
        <p>GPS Control © 2026. Todos los derechos reservados.</p>
      </footer>
    </main>
  );
}