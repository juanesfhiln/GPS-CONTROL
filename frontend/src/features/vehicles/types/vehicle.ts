
export interface Vehicle {
    id: number;
    name: string;
    latitude: number | null;
    longitude: number | null;
    speed: number;
    heading: number;
    heading_cardinal: string;
    altitude: number | null;
    position_time: string | null;
    last_update_time: string | null;
    status: string;
}

export interface VehiclesResponse {
    total: number;
    pagina: number;
    limite: number;
    total_paginas: number;
    resultados: Vehicle[];
}
