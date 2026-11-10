
import {
  apiFetch,
  establecerTokenCSRF
} from "../../../services/api";

import type {
  LoginRequest,
  LoginResponse,
  AuthUser
} from "../types/auth";

export async function login(
  datos: LoginRequest
): Promise<LoginResponse> {
  const resultado = await apiFetch<LoginResponse>(
    "/api/v1/auth/login",
    {
      method: "POST",
      body: JSON.stringify(datos),
    }
  );

  establecerTokenCSRF(resultado.csrf_token);

  return resultado;
}

export async function getCurrentUser(): Promise<AuthUser> {
  return apiFetch<AuthUser>("/api/v1/auth/me");
}

export async function recuperarTokenCSRF(): Promise<void> {
  const resultado = await apiFetch<{ csrf_token: string }>(
    "/api/v1/auth/csrf"
  );

  establecerTokenCSRF(resultado.csrf_token);
}

export async function logout(): Promise<void> {
  await apiFetch<void>("/api/v1/auth/logout", {
    method: "POST",
  });

  establecerTokenCSRF(null);
}

export interface PasswordChangeRequest {
  password_actual: string;
  password_nueva: string;
  confirmar_password: string;
}

export async function cambiarPassword(
  datos: PasswordChangeRequest
): Promise<{ mensaje: string; csrf_token: string }> {
  const resultado = await apiFetch<{
    mensaje: string;
    csrf_token: string;
  }>("/api/v1/auth/change-password", {
    method: "POST",
    body: JSON.stringify(datos),
  });

  establecerTokenCSRF(resultado.csrf_token);

  return resultado;
}
