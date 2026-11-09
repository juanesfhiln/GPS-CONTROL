import { getDrivers } from "./driverService";
import type { Driver } from "../types/driver";
import { descargarCSV } from "../../../services/csv";

export async function getAllDriversForExport(buscar?: string): Promise<Driver[]> {
    const primeraPagina = await getDrivers(1, 100, buscar);
    const conductores = [...primeraPagina.resultados];

    for (let pagina = 2; pagina <= primeraPagina.total_paginas; pagina++) {
        const respuesta = await getDrivers(pagina, 100, buscar);
        conductores.push(...respuesta.resultados);
    }

    return conductores;
}

export function exportDriversToCSV(conductores: Driver[]): void {
    descargarCSV(
        `conductores_${new Date().toISOString().slice(0, 10)}.csv`,
        ["ID", "Nombre", "Código", "Teléfono", "Descripción", "ID vehículo asignado", "Campos personalizados"],
        conductores.map((conductor) => [
            conductor.id,
            conductor.name,
            conductor.code ?? "",
            conductor.phone ?? "",
            conductor.description ?? "",
            conductor.assigned_unit_id ?? "",
            JSON.stringify(conductor.custom_fields ?? {})
        ])
    );
}
