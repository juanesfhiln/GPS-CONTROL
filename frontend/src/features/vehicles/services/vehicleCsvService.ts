
import type { Vehicle } from "../types/vehicle";

function escaparCSV(valor: unknown): string {
    const texto = String(valor ?? "");
    return `"${texto.replace(/"/g, '""')}"`;
}

export function exportVehiclesToCSV(vehiculos: Vehicle[]): void {
    if (vehiculos.length === 0) {
        throw new Error("No hay vehículos para exportar.");
    }

    const camposPersonalizados = new Map<string, string>();

    vehiculos.forEach((vehiculo) => {
        Object.entries(vehiculo.custom_fields ?? {}).forEach(([id, campo]) => {
            if (!camposPersonalizados.has(id)) {
                camposPersonalizados.set(
                    id,
                    campo.n || `Campo ${id}`
                );
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

    const filas = vehiculos.map((vehiculo) => {
        const campos = Array.from(camposPersonalizados.keys()).map((id) => {
            return vehiculo.custom_fields?.[id]?.v ?? "";
        });

        return [
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
            ...campos
        ];
    });

    const contenido = [
        encabezados.map(escaparCSV).join(","),
        ...filas.map((fila) => fila.map(escaparCSV).join(","))
    ].join("\r\n");

    const archivo = new Blob(
        ["\uFEFF", contenido],
        { type: "text/csv;charset=utf-8;" }
    );

    const url = URL.createObjectURL(archivo);
    const enlace = document.createElement("a");

    enlace.href = url;
    enlace.download = `vehiculos_${new Date().toISOString().slice(0, 10)}.csv`;

    document.body.appendChild(enlace);
    enlace.click();
    enlace.remove();

    URL.revokeObjectURL(url);
}
