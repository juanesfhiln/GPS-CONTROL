import { getPassengers } from "./passengerService";
import type { Passenger } from "../types/passenger";
import { descargarCSV } from "../../../services/csv";

export async function getAllPassengersForExport(buscar?: string): Promise<Passenger[]> {
    const primeraPagina = await getPassengers(1, 100, buscar);
    const pasajeros = [...primeraPagina.resultados];

    for (let pagina = 2; pagina <= primeraPagina.total_paginas; pagina++) {
        const respuesta = await getPassengers(pagina, 100, buscar);
        pasajeros.push(...respuesta.resultados);
    }

    return pasajeros;
}

export function exportPassengersToCSV(pasajeros: Passenger[]): void {
    descargarCSV(
        `pasajeros_${new Date().toISOString().slice(0, 10)}.csv`,
        ["ID", "Nombre", "Código", "Teléfono", "ID vehículo asignado", "Campos personalizados"],
        pasajeros.map((pasajero) => [
            pasajero.id,
            pasajero.name,
            pasajero.code ?? "",
            pasajero.phone ?? "",
            pasajero.assigned_unit_id ?? "",
            JSON.stringify(pasajero.custom_fields ?? {})
        ])
    );
}
