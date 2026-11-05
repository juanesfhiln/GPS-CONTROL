
import { useEffect, useState } from "react";
import { getBackendHealth, type BackendResponse } from "../services/api";
import StatusCard from "./StatusCard";

function BackendStatus() {
  const [backend, setBackend] = useState<BackendResponse | null>(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(false);

  const verificarBackend = async () => {
    setCargando(true);
    setError(false);

    try {
      const datos = await getBackendHealth();
      setBackend(datos);
    } catch {
      setBackend(null);
      setError(true);
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    verificarBackend();
  }, []);

  return (
    <section>
      <h2>Conexión con el servidor</h2>

      {cargando && <p>Estableciendo conexión con GPS Control API...</p>}

      {!cargando && backend && (
        <StatusCard
          titulo="Estado del servidor"
          estado={backend.status}
          descripcion={backend.mensaje}
        />
      )}

      {!cargando && error && (
        <p>No se pudo conectar con el backend.</p>
      )}

      <button onClick={verificarBackend} disabled={cargando}>
        {cargando ? "Comprobando..." : "Probar conexión"}
      </button>
    </section>
  );
}

export default BackendStatus;
