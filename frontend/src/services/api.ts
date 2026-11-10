
const apiUrlConfigurada = import.meta.env.VITE_API_URL?.trim();

export const API_URL = (
  apiUrlConfigurada || "http://localhost:8000"
).replace(/\/$/, "");

let csrfTokenEnMemoria: string | null = null;

export function establecerTokenCSRF(token: string | null): void {
  csrfTokenEnMemoria = token;
}

interface ApiOptions extends RequestInit {
  headers?: HeadersInit;
}

export interface BackendResponse {
  status: string;
  mensaje: string;
}

export async function apiFetch<T>(
  endpoint: string,
  opciones: ApiOptions = {}
): Promise<T> {
  const metodo = (opciones.method ?? "GET").toUpperCase();
  const headers = new Headers(opciones.headers);

  if (opciones.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  if (!["GET", "HEAD", "OPTIONS"].includes(metodo)) {
    if (csrfTokenEnMemoria) {
      headers.set("X-CSRF-Token", csrfTokenEnMemoria);
    }
  }

  const respuesta = await fetch(`${API_URL}${endpoint}`, {
    ...opciones,
    method: metodo,
    headers,
    credentials: "include",
  });

  if (!respuesta.ok) {
    if (respuesta.status === 401) {
      throw new Error("Sesión expirada o no autorizada");
    }

    if (respuesta.status === 403) {
      throw new Error("Acceso denegado o validación CSRF fallida");
    }

    throw new Error(`Error en la petición: ${respuesta.status}`);
  }

  if (respuesta.status === 204) {
    return undefined as T;
  }

  return respuesta.json() as Promise<T>;
}

export async function getBackendHealth(): Promise<BackendResponse> {
  return apiFetch<BackendResponse>("/health");
}
