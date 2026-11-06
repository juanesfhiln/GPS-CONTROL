
export interface LoginRequest {
  correo: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  usuario: string;
  correo: string;
  rol: string;
}

export interface AuthUser {
    id: number;
    nombre: string;
    correo: string;
    rol: string;
    activo: boolean;
    cambiar_password: boolean;
}