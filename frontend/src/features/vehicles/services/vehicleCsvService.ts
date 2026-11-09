import type { Vehicle } from "../types/vehicle";
import { descargarCSV } from "../../../services/csv";

export function exportVehiclesToCSV(vehiculos: Vehicle[]): void {
    const camposPersonalizados = new Map<string, string>();

    vehiculos.forEach((vehiculo) => {
        Object.entries(vehiculo.custom_fields ?? {}).forEach(([id, campo]) => {
            if (!camposPersonalizados.has(id)) {
                camposPersonalizados.set(id, campo.n || `Campo ${id}`);
            }
        });
    });

    const encabezados = [
        "ID",
        "Nombre",
        "Estado",
        "Velocidad",
        "Orientación",
        "Latitud",
        "Longitud",
        "Altitud",
        "Fecha de posición",
        "Último mensaje",
        ...Array.from(camposPersonalizados.values())
    ];

    const filas = vehiculos.map((vehiculo) => [
        vehiculo.id,
        vehiculo.name,
        vehiculo.status,
        vehiculo.speed,
        vehiculo.heading_cardinal ?? "",
        vehiculo.latitude ?? "",
        vehiculo.longitude ?? "",
        vehiculo.altitude ?? "",
        vehiculo.position_time ?? "",
        vehiculo.last_message_time ?? "",
        ...Array.from(camposPersonalizados.keys()).map(
            (id) => vehiculo.custom_fields?.[id]?.v ?? ""
        )
    ]);

    descargarCSV(
        `vehiculos_${new Date().toISOString().slice(0, 10)}.csv`,
        encabezados,
        filas
    );
}
