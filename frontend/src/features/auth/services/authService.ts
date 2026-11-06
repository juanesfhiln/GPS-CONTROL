
import { apiFetch } from "../../../services/api";

import type {
  LoginRequest,
  AuthUser
} from "../types/auth";

export interface LoginResponse {
  usuario: string;
  correo: string;
  rol: string;
}

export async function login(
  datos: LoginRequest
): Promise<LoginResponse> {
  return apiFetch<LoginResponse>("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify(datos),
  });
}

export async function getCurrentUser(): Promise<AuthUser> {
  return apiFetch<AuthUser>("/api/v1/auth/me");
}

export async function logout(): Promise<void> {
  await apiFetch<void>("/api/v1/auth/logout", {
    method: "POST",
  });
}

export interface PasswordChangeRequest {
  password_actual: string;
  password_nueva: string;
  confirmar_password: string;
}

export async function cambiarPassword(
  datos: PasswordChangeRequest
): Promise<{ mensaje: string }> {
  return apiFetch<{ mensaje: string }>("/api/v1/auth/change-password", {
    method: "POST",
    body: JSON.stringify(datos)
  });
}