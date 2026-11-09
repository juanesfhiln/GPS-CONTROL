export interface User {
    id: number;
    nombre: string;
    correo: string;
    activo: boolean;
    cambiar_password: boolean;
    rol: string;
}

export interface Role {
    id: number;
    nombre: string;
}

export interface UserCreate {
    nombre: string;
    correo: string;
    password: string;
    rol_id: number;
}

export interface UserUpdate {
    nombre?: string;
    correo?: string;
    rol_id?: number;
}