import { apiFetch } from "../../../services/api";

import type {
    PassengersResponse,
    PassengerPayload,
    PassengerOperationResponse
} from "../types/passenger";

export async function getPassengers(
    pagina = 1,
    limite = 10,
    buscar?: string
): Promise<PassengersResponse> {
    const parametros = new URLSearchParams({
        pagina: String(pagina),
        limite: String(limite)
    });

    if (buscar?.trim()) {
        parametros.set("buscar", buscar.trim());
    }

    return apiFetch<PassengersResponse>(
        `/api/v1/passengers/?${parametros.toString()}`,
        { cache: "no-store" }
    );
}

export async function createPassenger(
    datos: PassengerPayload
): Promise<PassengerOperationResponse> {
    return apiFetch<PassengerOperationResponse>(
        "/api/v1/passengers/",
        {
            method: "POST",
            body: JSON.stringify(datos)
        }
    );
}

export async function updatePassenger(
    passengerId: number,
    datos: PassengerPayload
): Promise<PassengerOperationResponse> {
    return apiFetch<PassengerOperationResponse>(
        `/api/v1/passengers/${passengerId}`,
        {
            method: "PUT",
            body: JSON.stringify(datos)
        }
    );
}

export async function deletePassenger(
    passengerId: number
): Promise<PassengerOperationResponse> {
    return apiFetch<PassengerOperationResponse>(
        `/api/v1/passengers/${passengerId}`,
        {
            method: "DELETE"
        }
    );
}

export async function assignPassenger(
    passengerId: number,
    unitId: number
): Promise<PassengerOperationResponse> {
    return apiFetch<PassengerOperationResponse>(
        `/api/v1/passengers/${passengerId}/asignar/${unitId}`,
        {
            method: "POST"
        }
    );
}

export async function unassignPassenger(
    passengerId: number,
    unitId: number
): Promise<PassengerOperationResponse> {
    return apiFetch<PassengerOperationResponse>(
        `/api/v1/passengers/${passengerId}/desvincular/${unitId}`,
        {
            method: "DELETE"
        }
    );
}