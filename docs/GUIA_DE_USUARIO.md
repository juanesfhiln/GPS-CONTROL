# Guía de usuario

## 1. Acceso

1. Abre la dirección del frontend.
2. Ingresa con el correo y contraseña asignados por el administrador.
3. Si la cuenta tiene activado el cambio obligatorio de contraseña, completa ese paso antes de acceder a los módulos.
4. Utiliza **Cerrar sesión** para terminar la sesión.

## 2. Módulos

- **Dashboard:** presenta indicadores generales de la operación.
- **Vehículos:** permite consultar las unidades disponibles. Al abrir una unidad se muestra su detalle y los campos personalizados.
- **Conductores:** permite consultar conductores y, según el rol, crear, editar, eliminar y asignar o desvincular conductores de vehículos.
- **Pasajeros:** permite consultar pasajeros y, según el rol, administrar sus datos y asignaciones.
- **Mapa:** muestra la ubicación de los vehículos disponibles desde la integración.
- **Historial de viajes:** permite consultar los recorridos históricos disponibles en Wialon para una unidad y un intervalo. La pantalla presenta los viajes, sus fechas y distancias, la ruta en el mapa y los controles de reproducción con indicadores de velocidad, tiempo y distancia. La disponibilidad depende de los datos históricos y permisos de Wialon. Si el intervalo contiene más de 10.000 mensajes, reduce el rango de fechas y vuelve a consultar.
- **Usuarios:** permite al administrador gestionar usuarios, roles, estado y restablecimiento de contraseña.
- **Auditoría:** permite al administrador consultar los registros de auditoría.

## 3. Roles y permisos

Los permisos se validan en el backend. Ocultar una opción en la interfaz no sustituye la autorización del servidor.

| Módulo/operación | Administrador | Operador | Visualizador |
|---|---:|---:|---:|
| Consultar dashboard | Sí | Sí | Sí |
| Consultar vehículos | Sí | Sí | Sí |
| Consultar campos personalizados | Sí | Sí | Sí |
| Crear, editar y eliminar campos personalizados | Sí | Sí | No |
| Consultar conductores y asignaciones | Sí | Sí | Sí |
| Crear, editar, eliminar y asignar conductores | Sí | Sí | No |
| Consultar pasajeros | Sí | Sí | Sí |
| Crear, editar, eliminar y asignar pasajeros | Sí | Sí | No |
| Consultar historial de viajes | Sí | Sí | Sí |
| Administrar usuarios y roles | Sí | No | No |
| Consultar auditoría | Sí | No | No |

## 4. Buenas prácticas

- No compartas credenciales ni dejes una sesión abierta en equipos compartidos.
- Verifica la unidad seleccionada antes de modificar campos o asignaciones.
- Confirma los datos antes de eliminar registros en Wialon.
- Verifica que el vehículo y el intervalo seleccionados correspondan a la consulta que necesitas. Si no aparecen viajes, comprueba que existan mensajes históricos en Wialon para ese periodo.
- Reporta al administrador errores de conexión, datos desactualizados o permisos inesperados.
