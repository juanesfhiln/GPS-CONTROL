
export interface Passenger {
    id: number;
    name: string;
    code: string | null;
    phone: string | null;
    assigned_unit_id: number | null;
    custom_fields: Record<string, string>;
}

export interface PassengersResponse {
    total: number;
    pagina: number;
    limite: number;
    total_paginas: number;
    resultados: Passenger[];
}

export interface PassengerPayload {
    name: string;
    code: string;
    phone: string;
    custom_fields: Record<string, string>;
}

export interface PassengerOperationResponse {
    mensaje: string;
    passenger_id?: number;
    unit_id?: number;
}
