
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
        return <p>Cargando conductores...</p>;
    }

    if (conductores.length === 0) {
        return <p>No se encontraron conductores.</p>;
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
                            <td>{conductor.id}</td>
                            <td>{conductor.name}</td>
                            <td>{conductor.code || "—"}</td>
                            <td>{conductor.phone || "—"}</td>

                            <td>
                                {conductor.assigned_unit_id ?? "Sin asignar"}
                            </td>

                            {puedeGestionar && (
                                <td className="drivers-table__actions">
                                    <button
                                        type="button"
                                        onClick={() => onEditar(conductor)}
                                    >
                                        Editar
                                    </button>

                                    <button
                                        type="button"
                                        onClick={() => onAsignar(conductor)}
                                    >
                                        {conductor.assigned_unit_id
                                            ? "Ver asignación"
                                            : "Asignar"}
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
