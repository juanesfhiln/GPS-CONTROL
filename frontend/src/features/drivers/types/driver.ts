
export interface Driver {
    id: number;
    name: string;
    code: string | null;
    phone: string | null;
    description: string | null;
    assigned_unit_id: number | null;
    custom_fields: Record<string, string>;
}

export interface DriversResponse {
    total: number;
    pagina: number;
    limite: number;
    total_paginas: number;
    resultados: Driver[];
}

export interface DriverAssignmentsResponse {
    total: number;
    resultados: DriverAssignment[];
    completa: boolean;
    vehiculos_con_error: number;
}

export interface DriverAssignment {
    unit_id: number;
    driver_id: string;
    name: string;
    phone: string;
}

export interface DriverPayload {
    name: string;
    code: string;
    phone: string;
    description: string;
}

export interface DriverOperationResponse {
    mensaje: string;
    id_wialon?: number;
    driver_id?: number;
    unit_id?: number;
}
