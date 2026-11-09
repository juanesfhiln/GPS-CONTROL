export function protegerValorCSV(valor: unknown): string {
    const texto = String(valor ?? "");
    const normalizado = texto.replace(/^[\s\u0000-\u001F]+/, "");
    const seguro = /^[=+\-@]/.test(normalizado)
        ? `'${texto}`
        : texto;

    return `"${seguro.replace(/"/g, '""')}"`;
}

export function descargarCSV(
    nombre: string,
    encabezados: string[],
    filas: unknown[][]
): void {
    if (filas.length === 0) {
        throw new Error("No hay registros para exportar.");
    }

    const contenido = [
        encabezados.map(protegerValorCSV).join(","),
        ...filas.map((fila) => fila.map(protegerValorCSV).join(","))
    ].join("\r\n");

    const archivo = new Blob(
        ["\uFEFF", contenido],
        { type: "text/csv;charset=utf-8;" }
    );

    const url = URL.createObjectURL(archivo);
    const enlace = document.createElement("a");

    enlace.href = url;
    enlace.download = nombre;
    document.body.appendChild(enlace);
    enlace.click();
    enlace.remove();
    URL.revokeObjectURL(url);
}
