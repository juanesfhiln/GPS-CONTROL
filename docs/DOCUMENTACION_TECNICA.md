# Documentación técnica

## 1. Tecnologías

| Capa | Tecnologías verificadas en el repositorio |
|---|---|
| Frontend | React 19, TypeScript, React Router, Vite 8, Sass, Recharts, Leaflet y React Leaflet. |
| Backend | Python, FastAPI, SQLAlchemy, Pydantic, PyJWT, pwdlib/Argon2, httpx y python-dotenv. |
| Persistencia | PostgreSQL mediante psycopg. |
| Migraciones | Alembic. |
| Pruebas | pytest y FastAPI TestClient. |
| Integración externa | API AJAX de Wialon mediante httpx asíncrono. |

## 2. Organización del backend

- `app/api/v1/`: routers HTTP de autenticación, usuarios, vehículos, conductores, pasajeros, dashboard, viajes y auditoría.
- `app/api/dependencies.py`: resolución del usuario autenticado y control de roles.
- `app/core/`: seguridad JWT y validación CSRF.
- `app/db/`: motor SQLAlchemy, sesiones y dependencias de base de datos.
- `app/domain/`: objetos de dominio de vehículos, conductores y pasajeros.
- `app/integrations/`: cliente Wialon, transformación de datos y proveedor simulado de viajes.
- `app/models/`: modelos persistidos de usuarios, roles y auditoría.
- `app/schemas/`: esquemas de entrada y salida.
- `app/services/`: lógica de negocio y coordinación con integraciones.
- `migrations/`: versiones de Alembic.
- `tests/`: pruebas API, unitarias y scripts de integración/diagnóstico.

## 3. Organización del frontend

El frontend separa páginas (`src/pages`), funcionalidades (`src/features`), servicios HTTP (`src/services`) y estilos Sass. `src/App.tsx` define las rutas y la protección de navegación. El contexto de autenticación mantiene el estado de sesión. Las solicitudes HTTP se centralizan en `src/services/api.ts`, que envía cookies mediante `credentials: include` y agrega la cabecera CSRF en operaciones de escritura cuando existe la cookie correspondiente.

## 4. Autenticación y seguridad

- JWT se firma con `JWT_SECRET_KEY` y `JWT_ALGORITHM`.
- La duración se controla con `ACCESS_TOKEN_EXPIRE_MINUTES`.
- Las contraseñas se procesan con `pwdlib` y su algoritmo recomendado (Argon2).
- El token de acceso se entrega en cookie `HttpOnly`; las opciones Secure y SameSite se configuran mediante variables de entorno.
- Las operaciones autenticadas por cookie utilizan protección CSRF y validación de origen.
- Se mantiene compatibilidad con autenticación Bearer para solicitudes que no usan cookie de sesión.
- La versión del token almacenada en el usuario permite invalidar sesiones.
- `require_roles` valida los roles permitidos en el servidor y responde con 403 cuando el rol no está autorizado.

## 5. Persistencia y migraciones

La conexión PostgreSQL se construye con `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` y `DB_NAME`. Las migraciones se ejecutan con Alembic desde `backend/`. El seed inicial crea los roles de aplicación y el usuario administrador. Los datos operativos de vehículos, conductores, pasajeros y recursos se consultan/gestionan a través de Wialon; los modelos locales incluyen usuarios, roles y auditoría.

## 6. Integración Wialon

`WialonClient` usa `WIALON_API_URL` y `WIALON_TOKEN`, gestiona la sesión y realiza solicitudes asíncronas. `WialonMapper` transforma las respuestas de unidades al modelo de dominio. `VehicleService` mantiene una caché temporal de vehículos y la invalida cuando se modifican campos personalizados. `WIALON_RESOURCE_ID` identifica el recurso utilizado por los servicios que operan sobre conductores y pasajeros.

El cliente Wialon se inicia y cierra mediante el ciclo de vida de FastAPI. Por esta razón, la configuración Wialon debe estar presente incluso para arrancar el backend local.

## 7. Endpoints principales

Todos los endpoints funcionales se montan bajo `/api/v1`. Los routers definen, entre otros, los siguientes recursos:

| Recurso | Operaciones principales |
|---|---|
| `/auth` | `POST /login`, `POST /logout`, `GET /me`, `POST /change-password`. |
| `/users` | `GET /roles`, `GET /`, `POST /`, `PUT /{usuario_id}`, `PATCH /{usuario_id}/estado`, `POST /{usuario_id}/restablecer-password`. |
| `/vehicles` | `GET /`, `GET /{unidad_id}/custom-fields`, `POST /{unidad_id}/custom-fields`, `PUT /{unidad_id}/custom-fields/{campo_id}`, `DELETE /{unidad_id}/custom-fields/{campo_id}`. |
| `/drivers` | Consulta, CRUD y asignación/desvinculación de conductores. |
| `/passengers` | Consulta, CRUD y asignación/desvinculación de pasajeros. |
| `/dashboard` | `GET /summary`. |
| `/trips` | `GET /{unidad_id}/history`. |
| `/audit` | `GET /`. |

La especificación interactiva puede consultarse en `/docs` mientras el backend está activo.

## 8. Viajes simulados

`TripService` utiliza `TripMockProvider`, que construye recorridos y métricas de ejemplo. Tanto los registros como la respuesta del historial llevan el indicador `simulated: true`. La integración de viajes con telemetría real no está implementada en esta versión.

## 9. Consideraciones de despliegue

- `frontend/src/services/api.ts` contiene actualmente `API_URL = "http://localhost:8000"`; requiere ajuste para un entorno remoto o una configuración de proxy.
- `FRONTEND_ORIGINS` debe reflejar el origen publicado del frontend.
- Utilizar HTTPS, `COOKIE_SECURE=true` y una política SameSite coherente con los dominios de despliegue.
- Proteger el `.env` y restringir los permisos de acceso a credenciales.
- Configurar Wialon con un token de alcance mínimo necesario.
- Evaluar división de código en el frontend: el build validado genera un chunk principal superior a 500 kB sin comprimir.
