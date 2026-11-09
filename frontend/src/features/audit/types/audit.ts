
export interface AuditLog {
    id: number;
    usuario_id: number | null;
    accion: string;
    modulo: string;
    descripcion: string;
    resultado: string;
    direccion_ip: string | null;
    fecha: string;
}

export interface AuditFilters {
    pagina: number;
    limite: number;
    usuario_id?: number;
    modulo?: string;
    resultado?: string;
}

export interface AuditListResponse {
    total: number;
    pagina: number;
    limite: number;
    total_paginas: number;
    resultados: AuditLog[];
}