import type { Passenger } from "../types/passenger";

interface PassengersTableProps {
    passengers: Passenger[];
    puedeAdministrar: boolean;
    onEdit: (passenger: Passenger) => void;
    onDelete: (passenger: Passenger) => void;
    onAssign: (passenger: Passenger) => void;
}

function PassengersTable({
    passengers,
    puedeAdministrar,
    onEdit,
    onDelete,
    onAssign
}: PassengersTableProps) {
    if (passengers.length === 0) {
        return <p className="passengers-empty">No se encontraron pasajeros.</p>;
    }

    return (
        <div className="passengers-table-container">
            <table className="passengers-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nombre</th>
                        <th>Código</th>
                        <th>Teléfono</th>
                        <th>Vehículo asignado</th>
                        {puedeAdministrar && <th>Acciones</th>}
                    </tr>
                </thead>

                <tbody>
                    {passengers.map(passenger => (
                        <tr key={passenger.id}>
                            <td data-label="ID">{passenger.id}</td>
                            <td data-label="Nombre">{passenger.name}</td>
                            <td data-label="Código">{passenger.code || "—"}</td>
                            <td data-label="Teléfono">{passenger.phone || "—"}</td>
                            <td data-label="Vehículo asignado">
                                {passenger.assigned_unit_id
                                    ? passenger.assigned_unit_id
                                    : "Sin asignar"}
                            </td>

                            {puedeAdministrar && (
                                <td className="passengers-table__actions" data-label="Acciones">
                                    <button type="button" onClick={() => onEdit(passenger)}>
                                        Editar
                                    </button>
                                    <button type="button" onClick={() => onAssign(passenger)}>
                                        Asignar
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => onDelete(passenger)}
                                        disabled={passenger.assigned_unit_id !== null}
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

export default PassengersTable;
