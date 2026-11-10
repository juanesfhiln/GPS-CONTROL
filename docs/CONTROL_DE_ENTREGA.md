# Control de entrega

## Documentación incluida

- [x] README principal con descripción, estructura, instalación, pruebas y consideraciones de despliegue.
- [x] Ejemplo de variables de entorno sin credenciales reales (`backend/.env.example`).
- [x] Guía de instalación y ejecución.
- [x] Guía de usuario y matriz de roles.
- [x] Documentación técnica de arquitectura, seguridad e integración.
- [x] Informe con los resultados de pruebas comunicados.

## Validaciones registradas

- [x] Suite backend: 208 aprobadas, 0 fallidas, 1 advertencia (ejecución local comunicada el 10/11/2026).
- [x] Historial RF-24: integración Wialon y validación funcional manual confirmada por el usuario.
- [ ] Repetir `npm run build` con la versión actual del frontend y registrar el resultado.
- [ ] Guardar capturas de evidencia del historial, filtros de vehículo/fechas y reproducción.
- [x] `.gitignore` del proyecto contempla entornos virtuales, archivos `.env`, cachés Python, dependencias y compilados.

## Pendientes de cierre de entrega

- [ ] Revisar `git status` y confirmar que solo se incluyan archivos de código, pruebas y documentación necesarios.
- [ ] Excluir archivos auxiliares locales que no formen parte de la entrega.
- [ ] Revisar los scripts de diagnóstico de `backend/tests/integration/` e identificar cuáles requieren credenciales Wialon.
- [ ] Confirmar que no existan secretos en archivos rastreados ni en el historial de Git. Si una credencial estuvo comprometida, rotarla; borrar el archivo en un commit no la elimina del historial.
- [ ] Repetir el build del frontend y registrar la salida.
- [ ] Guardar evidencias visuales de los módulos y del historial RF-24.
- [ ] Probar instalación limpia siguiendo `docs/INSTALACION.md` en un entorno separado.
- [ ] Revisar configuración de despliegue y confirmar que el frontend utiliza la URL correcta de API en producción.
- [ ] Preparar commit final de entrega y verificar el push a `origin/main`.

## Observaciones técnicas conocidas

- El historial de viajes ya consulta mensajes y viajes de Wialon; el cliente limita cada intervalo a 10.000 mensajes y no implementa paginación automática.
- La suite backend más reciente comunicada: 208 aprobadas, 0 fallidas y una advertencia deprecada de Starlette/httpx.
- El informe de build frontend disponible es anterior a los últimos cambios; se debe repetir la compilación.
- La configuración de API y los orígenes CORS deben verificarse para el despliegue final, sin asumir que los valores locales y de producción son intercambiables.
