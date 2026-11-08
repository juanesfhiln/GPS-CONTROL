
import { apiFetch } from "../../../services/api";
import type { VehiclesResponse } from "../types/vehicle";

export async function getVehicles(
    pagina = 1,
    limite = 100,
    buscar?: string
): Promise<VehiclesResponse> {
    const parametros = new URLSearchParams({
        pagina: String(pagina),
        limite: String(limite)
    });

    if (buscar?.trim()) {
        parametros.set("buscar", buscar.trim());
    }

    return apiFetch<VehiclesResponse>(
        `/api/v1/vehicles/?${parametros.toString()}`
    );
}
