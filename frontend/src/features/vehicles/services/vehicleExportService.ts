
import { getVehicles } from "./vehicleService";
import type { Vehicle } from "../types/vehicle";

export async function getAllVehiclesForExport(
    buscar?: string,
    estado?: string
): Promise<Vehicle[]> {
    const primeraPagina = await getVehicles(1, 100, buscar, estado);

    const vehiculos = [...primeraPagina.resultados];

    for (
        let pagina = 2;
        pagina <= primeraPagina.total_paginas;
        pagina++
    ) {
        const respuesta = await getVehicles(
            pagina,
            100,
            buscar,
            estado
        );

        vehiculos.push(...respuesta.resultados);
    }

    return vehiculos;
}
