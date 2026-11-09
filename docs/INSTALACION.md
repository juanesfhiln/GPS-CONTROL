# Instalación y ejecución

Esta guía corresponde a la estructura y configuración encontradas en la versión entregada. Los comandos están escritos para PowerShell en Windows.

## 1. Requisitos previos

- Python 3.11.
- PostgreSQL instalado y en ejecución.
- Node.js y npm.
- Token y URL de API de Wialon, además del identificador del recurso utilizado por la aplicación.

## 2. Preparar PostgreSQL

Crea una base de datos vacía llamada `gps_control` (o utiliza otro nombre y actualiza `DB_NAME` en el archivo de entorno). Por ejemplo, desde `psql` con un usuario que tenga permisos para crear bases de datos:

```sql
CREATE DATABASE gps_control;
```

Asegúrate de que el usuario configurado tenga permisos sobre esa base de datos.

## 3. Configurar el backend

Desde la raíz del repositorio:

```powershell
cd backend
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Edita `backend/.env` y completa los valores reales. No compartas ni subas ese archivo. Las variables utilizadas por el código son:

| Variable | Uso |
|---|---|
| `DB_USER` | Usuario de PostgreSQL. |
| `DB_PASSWORD` | Contraseña de PostgreSQL. |
| `DB_HOST` | Host de PostgreSQL. |
| `DB_PORT` | Puerto de PostgreSQL (por defecto, 5432). |
| `DB_NAME` | Nombre de la base de datos. |
| `JWT_SECRET_KEY` | Secreto para firmar tokens y validar tokens CSRF. |
| `JWT_ALGORITHM` | Algoritmo JWT; el código usa `HS256` por defecto. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duración del token en minutos (30 por defecto). |
| `COOKIE_SECURE` | Activa cookies Secure cuando es `true`. |
| `COOKIE_SAMESITE` | Política SameSite: `lax`, `strict` o `none`. `none` requiere `COOKIE_SECURE=true`. |
| `FRONTEND_ORIGINS` | Lista separada por comas de orígenes autorizados para CORS y CSRF. |
| `WIALON_API_URL` | URL del endpoint AJAX de Wialon. |
| `WIALON_TOKEN` | Token de acceso a Wialon. |
| `WIALON_RESOURCE_ID` | Identificador del recurso Wialon usado por módulos que consultan recursos. |
| `ADMIN_NAME` | Nombre del administrador inicial. |
| `ADMIN_EMAIL` | Correo del administrador inicial. |
| `ADMIN_PASSWORD` | Contraseña inicial del administrador. |

Genera un secreto JWT aleatorio. Por ejemplo, en PowerShell con Python:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copia el resultado como valor de `JWT_SECRET_KEY`. Define una contraseña de administrador propia y cambia las credenciales de ejemplo.

**Importante:** el cliente Wialon se construye al importar los servicios y la aplicación lo inicia en el ciclo de vida de FastAPI. Si faltan `WIALON_API_URL` o `WIALON_TOKEN`, el backend no inicia correctamente.

## 4. Crear las tablas y el administrador inicial

Con el entorno virtual activo y ubicado en `backend/`:

```powershell
alembic upgrade head
python -m app.seed
```

El comando `seed` crea los roles `Administrador`, `Operador` y `Visualizador` si no existen y registra el usuario administrador definido en el `.env`. Si el correo ya existe, no crea otro usuario.

## 5. Ejecutar el backend

Desde `backend/`:

```powershell
uvicorn app.main:app --reload
```

La API queda disponible en `http://localhost:8000`. Verifica `http://localhost:8000/health`. La documentación Swagger está en `http://localhost:8000/docs`.

## 6. Ejecutar el frontend

Abre otra terminal desde la raíz del repositorio:

```powershell
cd frontend
npm ci
npm run dev
```

Vite muestra la dirección local, normalmente `http://localhost:5173`. Esta dirección debe estar incluida en `FRONTEND_ORIGINS`. El frontend actualmente consume el backend desde `http://localhost:8000`, configurado directamente en `frontend/src/services/api.ts`.

## 7. Ejecutar las pruebas

Desde `backend/`:

```powershell
python -m pytest tests -q
```

No ejecutes automáticamente los scripts manuales de `tests/integration/` como parte de esta validación: algunos realizan llamadas a Wialon y requieren una configuración externa real.

Para validar la compilación del frontend, desde `frontend/`:

```powershell
npm run build
```

## 8. Problemas frecuentes

- `ModuleNotFoundError: No module named 'app'`: ejecuta pytest desde `backend/` usando `python -m pytest tests -q`.
- Error de conexión PostgreSQL: verifica servicio, host, puerto, usuario, contraseña y nombre de base de datos.
- Error por credenciales Wialon: verifica `WIALON_API_URL`, `WIALON_TOKEN` y permisos del token.
- Error 403 en operaciones de escritura: comprueba el origen autorizado y la cookie/cabecera CSRF cuando se utiliza autenticación por cookies; revisa también el rol del usuario.
- Frontend no conecta con API: confirma que FastAPI esté escuchando en el puerto 8000 y que `API_URL` en `frontend/src/services/api.ts` coincida con la dirección.
