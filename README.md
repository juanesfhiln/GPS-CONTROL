# GPS Control

Sistema web de gestión y monitoreo de flota vehicular, con integración de unidades y recursos de Wialon, administración de conductores y pasajeros, control de usuarios por roles y registro de auditoría.

## Contenido

- `backend/`: API REST construida con FastAPI, SQLAlchemy, PostgreSQL y Alembic.
- `frontend/`: aplicación web construida con React, TypeScript, Vite y Sass.
- `docs/`: guía de instalación, guía de uso, descripción técnica, pruebas y lista de entrega.

## Funcionalidades

- Inicio y cierre de sesión, validación de sesión y cambio obligatorio de contraseña cuando corresponda.
- Gestión de usuarios y roles: Administrador, Operador y Visualizador.
- Consulta de vehículos y detalle de unidad, con campos personalizados gestionados mediante Wialon.
- Gestión de conductores, pasajeros y sus asignaciones a vehículos.
- Dashboard con indicadores generales y mapa de vehículos.
- Consulta del historial de viajes mediante la integración con Wialon. La API obtiene los viajes y mensajes del intervalo consultado, transforma los datos para su visualización en mapa y reproducción, e identifica la respuesta con `simulated: false`.
- Registro y consulta de auditoría para las operaciones contempladas por el backend.

## Requisitos

- Python 3.11 (versión utilizada para las pruebas del proyecto).
- PostgreSQL.
- Node.js y npm compatibles con las versiones de Vite incluidas en `frontend/package-lock.json`.
- Acceso a una cuenta/servidor Wialon y su token de API. El backend inicializa el cliente Wialon al arrancar, por lo que las variables Wialon son necesarias para iniciar la aplicación.

## Instalación y configuración

Consulta [`docs/INSTALACION.md`](docs/INSTALACION.md) para crear el entorno, configurar PostgreSQL, completar las variables de entorno, ejecutar migraciones y arrancar ambos servicios.

## Uso

Consulta [`docs/GUIA_DE_USUARIO.md`](docs/GUIA_DE_USUARIO.md) para conocer los módulos de la interfaz y las diferencias de permisos entre roles.

## Arquitectura y API

La descripción de componentes, autenticación, autorización, integración y endpoints principales está en [`docs/DOCUMENTACION_TECNICA.md`](docs/DOCUMENTACION_TECNICA.md). Con el backend en ejecución, la documentación interactiva de la API está disponible en `http://localhost:8000/docs`.

## Pruebas y compilación

Desde `backend/`, con el entorno virtual activo:

```powershell
python -m pytest tests -q
```

Desde `frontend/`:

```powershell
npm run build
```

Los resultados de validación registrados para esta versión están en [`docs/INFORME_DE_PRUEBAS.md`](docs/INFORME_DE_PRUEBAS.md).

## Consideraciones antes de desplegar

- No subir `backend/.env`, tokens de Wialon, contraseñas ni claves JWT al repositorio.
- Generar una `JWT_SECRET_KEY` propia y robusta para cada entorno.
- Configurar `FRONTEND_ORIGINS` con los orígenes reales del frontend.
- En producción, utilizar HTTPS y `COOKIE_SECURE=true`; revisar también `COOKIE_SAMESITE` según el dominio y la arquitectura de despliegue.
- El frontend define actualmente `API_URL` como `http://localhost:8000` en `frontend/src/services/api.ts`. Para desplegar en otro host, debe ajustarse esa dirección o configurarse una estrategia de proxy compatible.
- La integración de Wialon depende de credenciales y recursos válidos. La disponibilidad real de datos depende de la cuenta y permisos configurados en Wialon.
- El historial de viajes consulta datos de Wialon. La disponibilidad y cobertura dependen de los permisos, datos históricos y límites de mensajes de la cuenta configurada. Los intervalos con más de 10.000 mensajes deben reducirse; la paginación automática de intervalos todavía no está implementada.

## Estado de validación

En la validación local comunicada más reciente se ejecutaron 208 pruebas del backend, todas aprobadas (0 fallidas), con una advertencia deprecada de Starlette/httpx. La compilación frontend registrada anteriormente completó correctamente; debe repetirse después de los últimos cambios para actualizar la evidencia de entrega. El frontend genera una advertencia por un bundle JavaScript principal superior a 500 kB; no impide la compilación, pero se recomienda evaluar división de código antes de optimizar el despliegue.
