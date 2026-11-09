
import { apiFetch } from "../../../services/api";
import type { TripHistoryResponse } from "../types/trip";

export async function getTripHistory(
    vehicleId: number,
    fechaInicio: string,
    fechaFin: string
): Promise<TripHistoryResponse> {
    const parametros = new URLSearchParams({
        fecha_inicio: fechaInicio,
        fecha_fin: fechaFin
    });

    return apiFetch<TripHistoryResponse>(
        `/api/v1/trips/${vehicleId}/history?${parametros.toString()}`
    );
}
