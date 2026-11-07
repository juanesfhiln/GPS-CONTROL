import { apiFetch } from "../../../services/api";

export interface DashboardSummary {
  total_vehiculos: number;
  en_movimiento: number;
  detenidos: number;
  sin_senal: number;
  vehiculos_con_ubicacion: number;
  velocidad_promedio: number;
  ultima_actualizacion: string | null;
}

export async function obtenerResumenDashboard(): Promise<DashboardSummary> {
  return apiFetch<DashboardSummary>("/api/v1/dashboard/summary");
}