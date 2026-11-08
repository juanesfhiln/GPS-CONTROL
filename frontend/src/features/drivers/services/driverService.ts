
import { apiFetch } from "../../../services/api";

import type {
    DriversResponse,
    DriverAssignmentsResponse,
    DriverPayload,
    DriverOperationResponse
} from "../types/driver";

export async function getDrivers(
    pagina = 1,
    limite = 10,
    buscar?: string
): Promise<DriversResponse> {
    const parametros = new URLSearchParams({
        pagina: String(pagina),
        limite: String(limite)
    });

    if (buscar?.trim()) {
        parametros.set("buscar", buscar.trim());
    }

    return apiFetch<DriversResponse>(
        `/api/v1/drivers/?${parametros.toString()}`,
        { cache: "no-store" }
    );
}

export async function getDriverAssignments():
    Promise<DriverAssignmentsResponse> {
    return apiFetch<DriverAssignmentsResponse>(
        "/api/v1/drivers/asignaciones"
    );
}

export async function createDriver(
    datos: DriverPayload
): Promise<DriverOperationResponse> {
    return apiFetch<DriverOperationResponse>(
        "/api/v1/drivers/",
        {
            method: "POST",
            body: JSON.stringify(datos)
        }
    );
}

export async function updateDriver(
    driverId: number,
    datos: DriverPayload
): Promise<DriverOperationResponse> {
    return apiFetch<DriverOperationResponse>(
        `/api/v1/drivers/${driverId}`,
        {
            method: "PUT",
            body: JSON.stringify(datos)
        }
    );
}

export async function deleteDriver(
    driverId: number
): Promise<DriverOperationResponse> {
    return apiFetch<DriverOperationResponse>(
        `/api/v1/drivers/${driverId}`,
        {
            method: "DELETE"
        }
    );
}

export async function assignDriver(
    driverId: number,
    unitId: number
): Promise<DriverOperationResponse> {
    return apiFetch<DriverOperationResponse>(
        `/api/v1/drivers/${driverId}/asignar/${unitId}`,
        {
            method: "POST"
        }
    );
}

export async function unassignDriver(
    driverId: number,
    unitId: number
): Promise<DriverOperationResponse> {
    return apiFetch<DriverOperationResponse>(
        `/api/v1/drivers/${driverId}/desvincular/${unitId}`,
        {
            method: "DELETE"
        }
    );
}
