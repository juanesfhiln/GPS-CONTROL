
const apiUrlConfigurada = import.meta.env.VITE_API_URL?.trim();

export const API_URL = (apiUrlConfigurada || "http://localhost:8000").replace(/\/$/, "");

export interface BackendResponse {
  status: string;
  mensaje: string;
}

function obtenerTokenCSRF(): string | null {
  const cookie = document.cookie
    .split("; ")
    .find((fila) => fila.startsWith("csrf_token="));

  return cookie
    ? decodeURIComponent(cookie.split("=").slice(1).join("="))
    : null;
}

interface ApiOptions extends RequestInit {
  headers?: HeadersInit;
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
    const csrfToken = obtenerTokenCSRF();

    if (csrfToken) {
      headers.set("X-CSRF-Token", csrfToken);
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
