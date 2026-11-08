
import { useEffect, useState } from "react";

import type {
    Driver,
    DriverPayload
} from "../types/driver";

interface DriverFormProps {
    conductor: Driver | null;
    guardando: boolean;
    onGuardar: (datos: DriverPayload) => Promise<void>;
    onCancelar: () => void;
}

function DriverForm({
    conductor,
    guardando,
    onGuardar,
    onCancelar
}: DriverFormProps) {
    const [nombre, setNombre] = useState("");
    const [codigo, setCodigo] = useState("");
    const [telefono, setTelefono] = useState("");
    const [descripcion, setDescripcion] = useState("");

    useEffect(() => {
        setNombre(conductor?.name ?? "");
        setCodigo(conductor?.code ?? "");
        setTelefono(conductor?.phone ?? "");
        setDescripcion(conductor?.description ?? "");
    }, [conductor]);

    async function enviarFormulario(
        evento: React.FormEvent<HTMLFormElement>
    ) {
        evento.preventDefault();

        await onGuardar({
            name: nombre.trim(),
            code: codigo.trim(),
            phone: telefono.trim(),
            description: descripcion.trim()
        });
    }

    return (
        <form onSubmit={enviarFormulario} className="driver-form">
            <h2>
                {conductor ? "Editar conductor" : "Nuevo conductor"}
            </h2>

            <label htmlFor="driver-name">Nombre *</label>
            <input
                id="driver-name"
                value={nombre}
                onChange={(e) => setNombre(e.target.value)}
                maxLength={100}
                required
            />

            <label htmlFor="driver-code">Código</label>
            <input
                id="driver-code"
                value={codigo}
                onChange={(e) => setCodigo(e.target.value)}
                maxLength={50}
            />

            <label htmlFor="driver-phone">Teléfono</label>
            <input
                id="driver-phone"
                value={telefono}
                onChange={(e) => setTelefono(e.target.value)}
                maxLength={30}
            />

            <label htmlFor="driver-description">Descripción</label>
            <textarea
                id="driver-description"
                value={descripcion}
                onChange={(e) => setDescripcion(e.target.value)}
                maxLength={250}
                rows={3}
            />

            <div className="driver-form__actions">
                <button
                    type="button"
                    onClick={onCancelar}
                    disabled={guardando}
                >
                    Cancelar
                </button>

                <button
                    type="submit"
                    disabled={guardando || !nombre.trim()}
                >
                    {guardando ? "Guardando..." : "Guardar"}
                </button>
            </div>
        </form>
    );
}

export default DriverForm;
