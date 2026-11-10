# Informe de pruebas y compilación

## 1. Alcance

Este informe registra los resultados compartidos durante la validación de la versión entregada. No representa una nueva ejecución realizada durante la preparación de esta documentación.

## 2. Backend

Comando ejecutado desde `backend/` con el entorno virtual activo:

```powershell
python -m pytest tests -q
```

Resultado comunicado:

- 208 pruebas aprobadas.
- 0 pruebas fallidas.
- 1 advertencia deprecada relacionada con el uso de `httpx` en `starlette.testclient`.
- Tiempo informado: 10.45 segundos.

La ejecución incluye tres pruebas unitarias nuevas de `TripService`, además de las pruebas del cliente Wialon. El resultado corresponde a la ejecución comunicada por el usuario el 10 de noviembre de 2026.

La advertencia no impidió la ejecución satisfactoria de la suite. Debe revisarse la compatibilidad futura de las dependencias de pruebas.

## 3. Frontend

Comando ejecutado desde `frontend/`:

```powershell
npm run build
```

Resultado comunicado:

- `tsc -b` completó correctamente.
- Vite transformó 2.588 módulos.
- Build finalizado correctamente en 1.58 segundos.
- `dist/index.html`: 0.45 kB (0.29 kB gzip).
- CSS: 64.19 kB (14.07 kB gzip).
- JavaScript: 871.29 kB (253.57 kB gzip).

Vite reportó que algunos chunks superan 500 kB tras minificación. Es una advertencia de rendimiento, no un error de compilación. Se recomienda evaluar carga diferida de páginas y división de código.

## 4. Validaciones funcionales comunicadas

Durante las pruebas manuales se reportó la validación de los siguientes comportamientos:

- Las solicitudes protegidas sin autenticación reciben 401.
- El Visualizador no puede ejecutar operaciones de escritura y recibe 403.
- El Operador no puede acceder a funciones exclusivas del Administrador.
- Se verificaron operaciones de creación, actualización, eliminación y asignación en módulos operativos, junto con consultas de auditoría.

## 5. Limitaciones y advertencias

- El historial de viajes se integró con `messages/load_interval` y `unit/get_trips` de Wialon. El usuario confirmó una prueba funcional en la interfaz: lista de viajes, mapa, controles de reproducción, velocidad, tiempo y distancia. Esta validación manual no sustituye una prueba automatizada contra Wialon ni acredita todos los intervalos y volúmenes posibles.
- Los scripts de `tests/integration/` pueden requerir conexión externa y credenciales Wialon. No deben ejecutarse indiscriminadamente en una suite automatizada.
- La advertencia de `httpx`/Starlette debe revisarse al actualizar dependencias.
- El cliente limita la carga a 10.000 mensajes por intervalo y solicita reducir el rango cuando se supera el límite; no hay paginación automática.
- La compilación frontend debe repetirse después de los últimos cambios para confirmar el estado actual.
- El tamaño del chunk JavaScript principal merece optimización posterior.
