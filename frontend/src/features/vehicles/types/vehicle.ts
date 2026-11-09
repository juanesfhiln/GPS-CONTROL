export interface VehicleCustomField {
    n: string;
    v: string;
    [key: string]: unknown;
}

export interface Vehicle {
    id: number;
    name: string;
    latitude: number | null;
    longitude: number | null;
    speed: number;
    heading: number | null;
    heading_cardinal: string | null;
    altitude: number | null;
    position_time: string | null;
    last_message_time: string | null;
    status: string;
    communication_status: "conectado" | "sin_señal";
    position_status: "actualizada" | "antigua" | "sin_posicion";
    custom_fields: Record<string, VehicleCustomField>;
}

export interface VehiclesResponse {
    total: number;
    pagina: number;
    limite: number;
    total_paginas: number;
    resultados: Vehicle[];
}