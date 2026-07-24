# Reglas de trabajo para `T4/Projecto`

## Fuente de verdad

LeFodigital es una aplicación multiusuario compuesta por Angular 22, FastAPI y
PostgreSQL. Antes de modificarla, leer:

- [Guía de despliegue y operación](README.md).
- [Plan final implementado](../IMPLEMENTATION_PLAN.md).
- [Contexto técnico, arquitectura y estado](CONTEXT.md).
- [Entrada del frontend](frontend/src/main.ts).
- [Rutas del frontend](frontend/src/app/app.routes.ts).
- [Entrada y composición del backend](backend/app/main.py).
- [Configuración de migraciones](backend/alembic/env.py).
- [Migración inicial](backend/alembic/versions/20260724_0001_initial_schema.py).

Estas reglas complementan las [reglas generales](../../AGENTS.md), el
[contexto general](../../CONTEXT.md), las [reglas de la Fase 4](../AGENTS.md)
y su [contexto académico](../CONTEXT.md).

## Organización obligatoria

- Mantener `frontend/` y `backend/` como aplicaciones independientes.
- Organizar Angular en `core`, `shared` y `features`; usar componentes
  standalone y carga diferida por rutas.
- Cada componente visual Angular debe separar `.ts`, `.html` y `.scss`. No
  usar templates ni estilos inline.
- Organizar FastAPI por módulos con `router.py`, `schemas.py` y `service.py`.
  Añadir repositories o adaptadores solo cuando exista persistencia o una
  dependencia sustituible que lo justifique.
- Mantener en inglés el código, nombres, contratos y comentarios técnicos.
  Mantener en español los textos visibles, errores destinados al usuario y la
  documentación operativa.
- Aplicar SOLID con pragmatismo. No introducir DDD, Clean Architecture,
  microservicios, colas, Redis o abstracciones sin un caso concreto.

## Persistencia y migraciones

- PostgreSQL es la fuente de verdad funcional; no guardar datos en
  `localStorage`.
- Gestionar todo cambio estructural con modelos SQLAlchemy 2 y migraciones
  Alembic revisadas.
- No usar `Base.metadata.create_all()` para evolucionar bases desplegadas.
- Después de modificar modelos, crear la migración, revisar su SQL y ejecutar
  `alembic check` contra PostgreSQL.
- Mantener las fechas en UTC y los identificadores públicos en UUID.
- La semilla debe ser idempotente y nunca restablecer usuarios existentes.
- Las evidencias se guardan en el volumen configurado; PostgreSQL conserva
  metadatos, propiedad y nombre interno.

## Seguridad

- No copiar secretos reales a código, documentación, pruebas, imágenes,
  commits, builds o `.env.example`.
- Desarrollo puede cargar un `.env` ignorado por Git. Producción, con
  `APP_ENV=prod`, recibe sus variables desde el despliegue y no carga `.env`.
- El access JWT permanece solo en memoria del frontend. El refresh JWT solo
  viaja en cookie HttpOnly y se rota en cada renovación.
- Toda autorización se valida en FastAPI aunque Angular oculte una acción.
- Nunca exponer rutas físicas del volumen ni servir evidencias directamente
  con Nginx.
- La clave OpenAI solo puede existir en el backend. No registrar prompts,
  respuestas, tokens o claves.
- Las credenciales demo son públicas por decisión académica explícita; no usar
  datos reales ni sensibles hasta retirarlas.
- La antigua clave Groq se considera comprometida y debe revocarse en el
  proveedor; borrarla del repositorio no la invalida.

## Compatibilidad funcional

- Conservar los roles `teacher` y `student`.
- Una actividad nueva es `draft`; el estudiante solo la ve después de
  publicarla.
- Completar no exige evidencia y concede puntos una sola vez.
- El nivel se calcula con `floor(points / 100) + 1`.
- Mantener las ocho medallas y evitar duplicados.
- Al eliminar actividades, retirar completions, metadatos y archivos, y
  recalcular puntos, nivel y medallas.
- El curso de una actividad es una relación opcional.
- La fecha límite es informativa.
- El chat es anónimo, temporal y limita historial, longitud y frecuencia.
- Mantener exportaciones PDF/XLSX con datos autorizados por la API.

## Calidad mínima

Antes de cerrar cambios:

1. Ejecutar `pytest` y mantener al menos 80 % de cobertura backend.
2. Ejecutar `pnpm test` y mantener 80 % en statements, funciones y líneas, y
   75 % en branches.
3. Ejecutar el build Angular de producción.
4. Verificar el SQL de Alembic y, cuando haya PostgreSQL disponible, aplicar la
   migración sobre `prj_grado_test` y ejecutar `alembic check`.
5. Revisar ambos roles, propiedad de evidencias, idempotencia, reportes y chat.
6. Verificar escritorio y anchos de 900 px y 560 px, teclado, foco, etiquetas,
   contraste y ausencia de desbordamiento.
7. Revisar que no se versionen `.env`, volúmenes, artefactos, cachés o secretos.
8. Actualizar [CONTEXT.md](CONTEXT.md) con resultados, riesgos y estado real.

## Despliegue y conservación

- Mantener solo `dev` y `prod` como ambientes desplegables.
- `docker-compose.dev.yml` puede cargar `.env`; `docker-compose.prod.yml` no
  puede usar `env_file`.
- El frontend de producción se sirve con Nginx y solo expone la aplicación y
  el proxy `/api`.
- El backend aplica migraciones y la semilla antes de iniciar, suponiendo una
  sola réplica inicial.
- No sobrescribir ni renombrar [URL pagina web.txt](<../URL%20pagina%20web.txt>).
- No cambiar el nombre histórico de la carpeta `Projecto`.
- Conservar trazabilidad con TRL5, GitHub, video, pruebas y Documento Maestro.
