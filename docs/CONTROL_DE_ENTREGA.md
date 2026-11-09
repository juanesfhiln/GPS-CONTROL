# Control de entrega

## Documentación incluida

- [x] README principal con descripción, estructura, instalación, pruebas y consideraciones de despliegue.
- [x] Ejemplo de variables de entorno sin credenciales reales (`backend/.env.example`).
- [x] Guía de instalación y ejecución.
- [x] Guía de usuario y matriz de roles.
- [x] Documentación técnica de arquitectura, seguridad e integración.
- [x] Informe con los resultados de pruebas comunicados.

## Validaciones registradas

- [x] Suite backend: 203 aprobadas, 0 fallidas, 1 advertencia.
- [x] Compilación frontend: correcta, con advertencia de chunk mayor a 500 kB.
- [x] `.gitignore` del proyecto contempla entornos virtuales, archivos `.env`, cachés Python, dependencias y compilados.

## Antes de publicar en Git

- [ ] Revisar `git status` y confirmar que solo se incluyan archivos de código, pruebas y documentación necesarios.
- [ ] Excluir archivos auxiliares locales como `revision.patch` y `pruebas_nuevas.zip`.
- [ ] Decidir si los scripts manuales de diagnóstico de `backend/tests/integration/` se conservan en el repositorio; documentar que algunos requieren Wialon.
- [ ] Confirmar que no existan secretos en archivos rastreados ni en el historial de Git. Si una credencial estuvo comprometida, rotarla; borrar el archivo en un commit no la elimina del historial.
- [ ] Crear el commit de entrega y verificar el push a `origin/main`.
- [ ] Probar instalación limpia siguiendo `docs/INSTALACION.md` en un entorno separado.

## Observaciones técnicas conocidas

- El historial de viajes usa `TripMockProvider` y genera información simulada.
- El frontend apunta a `http://localhost:8000` de forma fija en `frontend/src/services/api.ts`.
- El build muestra una advertencia por tamaño de chunk.
- La suite muestra una advertencia deprecada de Starlette/httpx.
