
import { apiFetch } from "../../../services/api";
import type {
    AuditFilters,
    AuditListResponse
} from "../types/audit";

export async function getAuditLogs(
    filtros: AuditFilters
): Promise<AuditListResponse> {
    const parametros = new URLSearchParams({
        pagina: String(filtros.pagina),
        limite: String(filtros.limite)
    });

    if (filtros.usuario_id !== undefined) {
        parametros.set("usuario_id", String(filtros.usuario_id));
    }

    if (filtros.modulo) {
        parametros.set("modulo", filtros.modulo);
    }

    if (filtros.resultado) {
        parametros.set("resultado", filtros.resultado);
    }

    return apiFetch<AuditListResponse>(
        `/api/v1/audit/?${parametros.toString()}`
    );
}
