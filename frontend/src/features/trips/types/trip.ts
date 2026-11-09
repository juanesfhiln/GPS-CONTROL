export interface TripRoutePoint {
    elapsed_seconds: number;
    latitude: number;
    longitude: number;
    speed: number;
}

export interface Trip {
    id: string;
    vehicle_id: number;
    start_time: string;
    end_time: string;
    duration_seconds: number;
    distance_km: number;
    start_latitude: number;
    start_longitude: number;
    end_latitude: number;
    end_longitude: number;
    average_speed: number;
    max_speed: number;
    route_points: TripRoutePoint[];
    simulated: boolean;
}

export interface TripHistoryResponse {
    vehicle_id: number;
    vehicle_name: string;
    fecha_inicio: string;
    fecha_fin: string;
    total_viajes: number;
    viajes: Trip[];
    simulated: boolean;
}