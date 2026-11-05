
export interface BackendResponse {
  status: string;
  mensaje: string;
}

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function getBackendHealth(): Promise<BackendResponse> {

  await delay(3000);
  
  const respuesta = await fetch("http://localhost:8000/health");

  if (!respuesta.ok) {
    throw new Error("Error al consultar el backend");
  }

  const datos: BackendResponse = await respuesta.json();

  return datos;
}
