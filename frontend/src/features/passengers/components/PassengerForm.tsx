import { useEffect, useState, type SyntheticEvent } from "react";
import type { Passenger, PassengerPayload } from "../types/passenger";

interface PassengerFormProps {
    passenger?: Passenger | null;
    guardando: boolean;
    onSubmit: (datos: PassengerPayload) => Promise<void>;
    onCancel: () => void;
}

interface CustomField {
    key: string;
    value: string;
}

function PassengerForm({ passenger, guardando, onSubmit, onCancel }: PassengerFormProps) {
    const [name, setName] = useState("");
    const [code, setCode] = useState("");
    const [phone, setPhone] = useState("");
    const [customFields, setCustomFields] = useState<CustomField[]>([]);
    const [error, setError] = useState("");

    useEffect(() => {
        setName(passenger?.name ?? "");
        setCode(passenger?.code ?? "");
        setPhone(passenger?.phone ?? "");
        setCustomFields(
            Object.entries(passenger?.custom_fields ?? {}).map(([key, value]) => ({
                key,
                value
            }))
        );
        setError("");
    }, [passenger]);

    function actualizarCampo(index: number, propiedad: keyof CustomField, valor: string) {
        setCustomFields(actuales =>
            actuales.map((campo, i) =>
                i === index ? { ...campo, [propiedad]: valor } : campo
            )
        );
    }

    function agregarCampo() {
        setCustomFields(actuales => [...actuales, { key: "", value: "" }]);
    }

    function eliminarCampo(index: number) {
        setCustomFields(actuales => actuales.filter((_, i) => i !== index));
    }

    async function manejarEnvio(event: SyntheticEvent<HTMLFormElement>) {
        event.preventDefault();

        if (guardando) return;
        setError("");

        const campos = customFields
            .filter(campo => campo.key.trim())
            .map(campo => ({
                key: campo.key.trim(),
                value: campo.value.trim()
            }));

        const claves = campos.map(campo => campo.key);

        if (new Set(claves).size !== claves.length) {
            setError("No puedes registrar campos personalizados con nombres repetidos.");
            return;
        }

        try {
            const datos: PassengerPayload = {
                name: name.trim(),
                code: code.trim(),
                phone: phone.trim(),
                custom_fields: Object.fromEntries(
                    campos.map(campo => [campo.key, campo.value])
                )
            };

            await onSubmit(datos);
        } catch (error) {
            setError(error instanceof Error ? error.message : "No fue posible guardar el pasajero.");
        }
    }

    return (
        <form className="passenger-form" onSubmit={manejarEnvio}>
            <h2>{passenger ? "Editar pasajero" : "Registrar pasajero"}</h2>

            <label htmlFor="passenger-name">Nombre</label>
            <input
                id="passenger-name"
                value={name}
                onChange={event => setName(event.target.value)}
                required
                maxLength={100}
            />

            <label htmlFor="passenger-code">Código</label>
            <input
                id="passenger-code"
                value={code}
                onChange={event => setCode(event.target.value)}
                maxLength={50}
            />

            <label htmlFor="passenger-phone">Teléfono</label>
            <input
                id="passenger-phone"
                value={phone}
                onChange={event => setPhone(event.target.value)}
                maxLength={30}
            />

            <section className="passenger-form__custom-fields">
                <h3>Campos personalizados</h3>

                {customFields.map((campo, index) => (
                    <div className="passenger-form__custom-field" key={index}>
                        <input
                            aria-label="Nombre del campo"
                            placeholder="Nombre del campo"
                            value={campo.key}
                            onChange={event =>
                                actualizarCampo(index, "key", event.target.value)
                            }
                        />

                        <input
                            aria-label="Valor del campo"
                            placeholder="Valor"
                            value={campo.value}
                            onChange={event =>
                                actualizarCampo(index, "value", event.target.value)
                            }
                        />

                        <button
                            type="button"
                            onClick={() => eliminarCampo(index)}
                        >
                            Eliminar
                        </button>
                    </div>
                ))}

                <button type="button" onClick={agregarCampo}>
                    Agregar campo
                </button>
            </section>

            {error && <p className="form-error">{error}</p>}

            <div className="passenger-form__actions">
                <button type="button" onClick={onCancel} disabled={guardando}>
                    Cancelar
                </button>

                <button type="submit" disabled={guardando}>
                    {guardando ? "Guardando..." : "Guardar pasajero"}
                </button>
            </div>
        </form>
    );
}

export default PassengerForm;