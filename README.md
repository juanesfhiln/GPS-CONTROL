# GPS Control

Sistema web de gestión y monitoreo de flota vehicular, con integración de unidades y recursos de Wialon, administración de conductores y pasajeros, control de usuarios por roles y registro de auditoría.

## Contenido

- `backend/`: API REST construida con FastAPI, SQLAlchemy, PostgreSQL y Alembic.
- `frontend/`: aplicación web construida con React, TypeScript, Vite y Sass.
- `docs/`: guía de instalación, guía de uso, descripción técnica e informe de pruebas.

## Funcionalidades

- Inicio y cierre de sesión, validación de sesión y cambio obligatorio de contraseña cuando corresponda.
- Gestión de usuarios y roles: Administrador, Operador y Visualizador.
- Consulta de vehículos y detalle de unidad, con campos personalizados gestionados mediante Wialon.
- Gestión de conductores, pasajeros y sus asignaciones a vehículos.
- Dashboard con indicadores generales y mapa de vehículos.
- Consulta del historial de viajes mediante Wialon. La API transforma los viajes y mensajes para su visualización en mapa y reproducción; la respuesta identifica los datos como no simulados.
- Registro y consulta de auditoría para las operaciones contempladas por el backend.
- Exportación CSV de vehículos, conductores y pasajeros, con controles de permisos y sanitización.

## Requisitos

- Python 3.11.
- PostgreSQL.
- Node.js y npm compatibles con las versiones fijadas en `frontend/package-lock.json`.
- Acceso a una cuenta/servidor Wialon y su token de API. El backend inicializa el cliente Wialon al arrancar, por lo que las variables Wialon son necesarias para iniciar la aplicación.

## Instalación y configuración

Consulta [`docs/INSTALACION.md`](docs/INSTALACION.md) para crear el entorno, configurar PostgreSQL, completar las variables de entorno, ejecutar migraciones y arrancar ambos servicios.

## Uso

Consulta [`docs/GUIA_DE_USUARIO.md`](docs/GUIA_DE_USUARIO.md) para conocer los módulos de la interfaz y las diferencias de permisos entre roles.

## Arquitectura y API

La descripción de componentes, autenticación, autorización, integración y endpoints principales está en [`docs/DOCUMENTACION_TECNICA.md`](docs/DOCUMENTACION_TECNICA.md). Con el backend en ejecución, la documentación interactiva de la API está disponible en `/docs`.

## Pruebas y compilación

Desde `backend/`, con el entorno virtual activo:

```powershell
python -m pytest tests -q
```

Desde `frontend/`:

```powershell
npm run build
npm audit
```

El informe de resultados y sus limitaciones está en [`docs/INFORME_DE_PRUEBAS.md`](docs/INFORME_DE_PRUEBAS.md). Los resultados históricos no sustituyen una ejecución posterior a cambios de código o dependencias.

## Seguridad

La aplicación aplica controles en varias capas: autenticación, autorización en el backend, protección de sesión, validación de datos y restricciones de configuración.

### Controles implementados y considerados

- **Autenticación:** contraseñas procesadas con `pwdlib` y su algoritmo recomendado (Argon2); JWT firmado con una clave configurada por entorno.
- **Sesiones:** cookie de acceso `HttpOnly`, opciones `Secure` y `SameSite` configurables, expiración del token y versión de token por usuario para revocar sesiones.
- **CSRF y origen:** protección CSRF para operaciones autenticadas mediante cookie y validación de orígenes permitidos.
- **Autorización:** dependencias del backend verifican autenticación y roles permitidos. El frontend no debe considerarse una frontera de seguridad.
- **Persistencia:** SQLAlchemy/ORM y esquemas de validación para las operaciones de datos.
- **Auditoría:** registro de operaciones contempladas por el módulo de auditoría.
- **Secretos:** credenciales y claves se suministran mediante variables de entorno; los archivos `.env` no deben versionarse.
- **Integración externa:** el frontend consume la API propia; las credenciales Wialon permanecen en el backend.

### Modelado inicial de amenazas (SEG-04)

Este modelo identifica activos, amenazas y controles principales. Es una primera evaluación cualitativa, no una certificación ni una prueba de penetración. Los controles marcados como pendientes requieren comprobación adicional antes de considerarse cerrados.

| Activo / límite de confianza | Amenaza y posible impacto | Controles existentes o previstos | Riesgo residual / validación pendiente |
|---|---|---|---|
| Cuentas de usuario y sesiones | Robo, falsificación o reutilización de credenciales para acceder a la plataforma. | Hash de contraseñas, JWT firmado, expiración, cookie `HttpOnly`, versión de token y revocación al modificar/desactivar usuarios. | Verificar rate limiting y bloqueo temporal del login; revisar política de contraseñas y configuración de cookies en producción. |
| Funciones y datos según rol | Un usuario intenta ejecutar operaciones administrativas u operaciones de escritura que no le corresponden. | Roles Administrador, Operador y Visualizador; validación de rol en el backend mediante dependencias; pruebas de autorización reportadas. | Revisar cada endpoint y probar acceso directo por ID para descartar IDOR y acceso cruzado a recursos. |
| Datos de vehículos, conductores y pasajeros | Entrada malformada o manipulada que provoque corrupción, acceso indebido o fallos. | Esquemas de validación y acceso a base de datos mediante SQLAlchemy/ORM; validaciones funcionales en servicios. | Revisar validaciones de todos los endpoints, límites de entrada y escape de salida en la interfaz. |
| Sesión basada en cookies | Una página externa intenta ejecutar acciones en nombre de un usuario autenticado. | Protección CSRF con token HMAC, cookie y cabecera de solicitud; validación de origen y CORS configurado. | Volver a probar flujos de escritura y revisar configuración SameSite/Secure en los dominios desplegados. |
| Token y datos de Wialon | Exposición del token o uso de un destino remoto no autorizado. | Token configurado en el backend mediante entorno; frontend no se comunica directamente con Wialon; host configurado por servidor. | Comprobar que ninguna ruta permita controlar URL/host Wialon y revisar redacción de logs y manejo de errores. |
| Datos exportados | Celdas CSV manipuladas para ejecutar fórmulas al abrir el archivo en una hoja de cálculo. | Sanitización CSV y permisos para exportar. | Probar valores que comiencen con caracteres de fórmula y verificar el archivo resultante. |
| Registros de auditoría | Alteración, consulta no autorizada o exposición de datos sensibles en eventos registrados. | Módulo de auditoría y acceso administrativo al endpoint de consulta. | Verificar que los eventos cubran las operaciones sensibles, que no almacenen secretos y que no puedan modificarse por usuarios no autorizados. |
| Configuración y dependencias | Secretos publicados, dependencias vulnerables o configuración insegura en producción. | Variables de entorno, `.gitignore`, Gitleaks, Dependabot y auditorías de dependencias realizadas. | Repetir auditorías en el entorno limpio con herramientas actualizadas; verificar cabeceras HTTP, modo debug y documentación de API en producción. |

### Principio de mínimo privilegio

Los permisos deben limitarse a lo necesario para cada función:

- **Administrador:** administra usuarios y roles, consulta auditoría y realiza las operaciones funcionales autorizadas.
- **Operador:** realiza operaciones de gestión sobre vehículos y recursos operativos, sin administrar usuarios ni consultar funciones exclusivas de auditoría.
- **Visualizador:** consulta dashboard, mapa, vehículos, conductores, pasajeros e historial; no debe crear, modificar, eliminar, asignar ni exportar datos.

La autorización debe verificarse en el backend en cada endpoint protegido. Ocultar botones o rutas en el frontend mejora la experiencia, pero no sustituye el control del servidor.

**Pendientes del modelado:** validar permisos por objeto/recurso (IDOR), cobertura de eventos de auditoría, rate limiting, cabeceras de seguridad, protección de logs y restricciones del destino Wialon. No se debe interpretar esta tabla como evidencia de que esas verificaciones ya se completaron.

## Consideraciones de despliegue

- No subir `backend/.env`, tokens de Wialon, contraseñas ni claves JWT al repositorio.
- Generar una `JWT_SECRET_KEY` propia, aleatoria y robusta para cada entorno.
- Configurar `FRONTEND_ORIGINS` con los orígenes reales del frontend.
- En producción, utilizar HTTPS y `COOKIE_SECURE=true`; revisar también `COOKIE_SAMESITE` según los dominios y la arquitectura de despliegue.
- Configurar `VITE_API_URL` con la URL del backend en cada entorno de despliegue.
- La integración de Wialon depende de credenciales, permisos y recursos válidos de la cuenta configurada.
- El historial de viajes admite hasta 10.000 mensajes por intervalo. Los rangos que superen el límite deben reducirse; la paginación automática todavía no está implementada.
- Los planes gratuitos de alojamiento pueden suspender servicios por inactividad. Verificar que la interfaz comunique el arranque en frío y gestione los reintentos.

## Estado de validación

- **Backend:** se reportaron 208 pruebas aprobadas y 0 fallidas en la suite ejecutada desde `backend/`. Tras incorporar `httpx2==2.16.0` a `requirements-dev.txt`, se informó una ejecución sin la advertencia previa de Starlette/httpx. La instalación limpia temporal más reciente instaló las dependencias declaradas correctamente, pero una ejecución de pytest desde la raíz no encontró el módulo `app`; la prueba debe repetirse desde `backend/` en ese entorno.
- **Dependencias backend:** en el entorno original, `pip-audit` quedó sin vulnerabilidades conocidas después de actualizar setuptools. En el entorno limpio temporal se detectaron versiones iniciales antiguas de pip y setuptools; la auditoría final de ese entorno queda pendiente tras actualizarlas.
- **Frontend:** una compilación anterior completó correctamente. Debe repetirse después de los últimos cambios. Se reportó un chunk JavaScript principal superior a 500 kB; es una advertencia de optimización, no un fallo de compilación.
- **Seguridad del repositorio:** Gitleaks no encontró secretos en el historial local analizado; GitHub Secret Scanning y Dependabot mostraron cero alertas en la revisión reportada. Estos resultados no garantizan detección absoluta de todos los secretos o vulnerabilidades.
- **Historial Wialon:** se probó funcionalmente en la interfaz, pero la cobertura de intervalos extensos está limitada por el máximo de 10.000 mensajes y la ausencia de paginación automática.

## Declaración de uso de IA

Se utilizó ChatGPT como herramienta de apoyo para analizar los requerimientos, revisar resultados de pruebas y auditorías, diagnosticar problemas técnicos y apoyar la organización y redacción de documentación. La implementación, revisión y validación final del código corresponden al autor del proyecto, quien debe poder explicar las decisiones y los componentes durante la defensa técnica.
