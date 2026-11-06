
const API_URL = "http://localhost:8000";

export interface BackendResponse {
  status: string;
  mensaje: string;
}

export async function getBackendHealth(): Promise<BackendResponse> {
  const respuesta = await fetch(`${API_URL}/health`);

  if (!respuesta.ok) {
    throw new Error("Error al consultar el backend");
  }

  const datos: BackendResponse = await respuesta.json();

  return datos;
}
