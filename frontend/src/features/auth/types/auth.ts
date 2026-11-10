
export interface LoginRequest {
  correo: string;
  password: string;
}

export interface LoginResponse {
  usuario: string;
  correo: string;
  rol: string;
  csrf_token: string;
}

export interface AuthUser {
  id: number;
  nombre: string;
  correo: string;
  rol: string;
  activo: boolean;
  cambiar_password: boolean;
}
