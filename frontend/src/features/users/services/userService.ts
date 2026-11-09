import { apiFetch } from "../../../services/api";

import type {
    User,
    Role,
    UserCreate,
    UserUpdate
} from "../types/user";

export async function listarUsuarios(): Promise<User[]> {
    return apiFetch<User[]>("/api/v1/users/");
}

export async function listarRoles(): Promise<Role[]> {
    return apiFetch<Role[]>("/api/v1/users/roles");
}

export async function crearUsuario(datos: UserCreate): Promise<User> {
    return apiFetch<User>("/api/v1/users/", {
        method: "POST",
        body: JSON.stringify(datos)
    });
}

export async function actualizarUsuario(
    usuarioId: number,
    datos: UserUpdate
): Promise<User> {
    return apiFetch<User>(`/api/v1/users/${usuarioId}`, {
        method: "PUT",
        body: JSON.stringify(datos)
    });
}

export async function cambiarEstadoUsuario(
    usuarioId: number
): Promise<User> {
    return apiFetch<User>(`/api/v1/users/${usuarioId}/estado`, {
        method: "PATCH"
    });
}

export interface PasswordResetResponse {
    mensaje: string;
    password_temporal: string;
}

export async function restablecerPasswordUsuario(
    usuarioId: number
): Promise<PasswordResetResponse> {
    return apiFetch<PasswordResetResponse>(
        `/api/v1/users/${usuarioId}/restablecer-password`,
        {
            method: "POST"
        }
    );
}