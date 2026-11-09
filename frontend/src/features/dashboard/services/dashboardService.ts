
import { apiFetch } from "../../../services/api";

export interface DashboardSummary {
  total_vehiculos: number;
  total_conductores: number;
  total_pasajeros: number;
  en_movimiento: number;
  detenidos: number;
  sin_senal: number;
  vehiculos_con_ubicacion: number;
  velocidad_promedio: number;
  vehiculos_con_conductor: number;
  vehiculos_sin_conductor: number;
  ultima_actualizacion: string | null;
  distribucion_estados: {
    en_movimiento: number;
    detenidos: number;
    sin_senal: number;
  };
  distribucion_conductores: {
    con_conductor: number;
    sin_conductor: number;
  };
}

export async function obtenerResumenDashboard(): Promise<DashboardSummary> {
  return apiFetch<DashboardSummary>("/api/v1/dashboard/summary");
}
