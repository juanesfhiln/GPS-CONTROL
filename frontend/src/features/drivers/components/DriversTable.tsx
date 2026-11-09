import type { Driver } from "../types/driver";

interface DriversTableProps {
    conductores: Driver[];
    puedeGestionar: boolean;
    cargando: boolean;
    onEditar: (conductor: Driver) => void;
    onEliminar: (conductor: Driver) => void;
    onAsignar: (conductor: Driver) => void;
}

function DriversTable({
    conductores,
    puedeGestionar,
    cargando,
    onEditar,
    onEliminar,
    onAsignar
}: DriversTableProps) {
    if (cargando) {
        return <p className="drivers-table__message">Cargando conductores...</p>;
    }

    if (conductores.length === 0) {
        return <p className="drivers-table__message">No se encontraron conductores.</p>;
    }

    return (
        <div className="drivers-table__container">
            <table className="drivers-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nombre</th>
                        <th>Código</th>
                        <th>Teléfono</th>
                        <th>Vehículo asignado</th>
                        {puedeGestionar && <th>Acciones</th>}
                    </tr>
                </thead>

                <tbody>
                    {conductores.map((conductor) => (
                        <tr key={conductor.id}>
                            <td data-label="ID">{conductor.id}</td>
                            <td data-label="Nombre">{conductor.name}</td>
                            <td data-label="Código">{conductor.code || "—"}</td>
                            <td data-label="Teléfono">{conductor.phone || "—"}</td>
                            <td data-label="Vehículo asignado">
                                {conductor.assigned_unit_id ?? "Sin asignar"}
                            </td>

                            {puedeGestionar && (
                                <td className="drivers-table__actions" data-label="Acciones">
                                    <button type="button" onClick={() => onEditar(conductor)}>
                                        Editar
                                    </button>
                                    <button type="button" onClick={() => onAsignar(conductor)}>
                                        {conductor.assigned_unit_id ? "Ver asignación" : "Asignar"}
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => onEliminar(conductor)}
                                        disabled={conductor.assigned_unit_id !== null}
                                    >
                                        Eliminar
                                    </button>
                                </td>
                            )}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default DriversTable;
