
import { apiFetch } from "../../../services/api";
import type { VehiclesResponse } from "../types/vehicle";

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

export async function updateVehicleCustomField(
    unidadId: number,
    campoId: number,
    nombre: string,
    valor: string
): Promise<{ mensaje: string; resultado: unknown }> {
    return apiFetch(
        `/api/v1/vehicles/${unidadId}/custom-fields/${campoId}`,
        {
            method: "PUT",
            body: JSON.stringify({
                nombre,
                valor
            })
        }
    );
}