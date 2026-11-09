
import { apiFetch } from "../../../services/api";
import type { VehiclesResponse } from "../types/vehicle";

export interface VehicleCustomField {
    id: number;
    nombre: string;
    valor: string;
}

export interface VehicleCustomFieldResponse {
    mensaje: string;
    resultado: unknown;
}

export async function getVehicles(
    pagina = 1,
    limite = 100,
    buscar?: string,
    estado?: string
): Promise<VehiclesResponse> {
    const parametros = new URLSearchParams({
        pagina: String(pagina),
        limite: String(limite)
    });

    if (buscar?.trim()) {
        parametros.set("buscar", buscar.trim());
    }

    if (estado && estado !== "todos") {
        parametros.set("estado", estado);
    }

    return apiFetch<VehiclesResponse>(
        `/api/v1/vehicles/?${parametros.toString()}`
    );
}

export async function getVehicleCustomFields(
    unidadId: number
): Promise<VehicleCustomField[]> {
    return apiFetch<VehicleCustomField[]>(
        `/api/v1/vehicles/${unidadId}/custom-fields`
    );
}

export async function createVehicleCustomField(
    unidadId: number,
    nombre: string,
    valor: string
): Promise<VehicleCustomFieldResponse> {
    return apiFetch<VehicleCustomFieldResponse>(
        `/api/v1/vehicles/${unidadId}/custom-fields`,
        {
            method: "POST",
            body: JSON.stringify({ nombre, valor })
        }
    );
}

export async function updateVehicleCustomField(
    unidadId: number,
    campoId: number,
    nombre: string,
    valor: string
): Promise<VehicleCustomFieldResponse> {
    return apiFetch<VehicleCustomFieldResponse>(
        `/api/v1/vehicles/${unidadId}/custom-fields/${campoId}`,
        {
            method: "PUT",
            body: JSON.stringify({ nombre, valor })
        }
    );
}

export async function deleteVehicleCustomField(
    unidadId: number,
    campoId: number
): Promise<VehicleCustomFieldResponse> {
    return apiFetch<VehicleCustomFieldResponse>(
        `/api/v1/vehicles/${unidadId}/custom-fields/${campoId}`,
        {
            method: "DELETE"
        }
    );
}
