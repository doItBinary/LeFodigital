# LeFodigital

LeFodigital es una plataforma educativa orientada al fortalecimiento de
competencias digitales básicas en comunidades educativas rurales. La aplicación
permite gestionar actividades, evidencias, cursos, recursos, reportes,
gamificación y acompañamiento mediante LeFoBot, con separación de permisos para
profesor y estudiante.

El proyecto fue construido como una aplicación web multiusuario con Angular 22,
FastAPI y PostgreSQL, siguiendo una organización modular, persistencia en base
de datos y ejecución reproducible mediante contenedores.

## Propósito académico

Este repositorio corresponde al componente práctico del curso Proyecto de
Grado. Su propósito es demostrar un prototipo funcional en nivel TRL5, con una
arquitectura capaz de sostener usuarios, datos persistentes, evidencias y
validaciones automatizadas.

El sistema se enfoca en:

- facilitar el acceso a actividades de alfabetización digital;
- permitir que el docente publique actividades y consulte evidencias;
- permitir que el estudiante complete actividades y haga seguimiento de su
  progreso;
- conservar información en PostgreSQL y archivos en un volumen persistente;
- generar reportes exportables;
- mantener separación entre interfaz, API, datos y configuración.

## Funciones principales

- Registro e inicio de sesión para profesor y estudiante.
- Registro docente protegido mediante código de invitación.
- Sesión con access JWT en memoria y refresh token en cookie HttpOnly.
- Gestión de cursos y actividades.
- Publicación de actividades para estudiantes.
- Carga y descarga autorizada de evidencias.
- Sistema de puntos, niveles y ocho medallas.
- Blog con publicaciones y comentarios.
- Perfil de usuario y mensajes de contacto.
- Reportes en PDF y Excel.
- Recursos educativos, simulaciones externas y LeFoBot.
- Interfaz responsive para escritorio, 900 px y 560 px.

## Arquitectura

```text
Navegador -> Angular/Nginx -> FastAPI -> PostgreSQL
                                  |-> Volumen de evidencias
                                  |-> OpenAI Responses API
```

La solución está separada en dos aplicaciones:

- `frontend`: Angular 22, componentes standalone, rutas diferidas, Vitest y
  Nginx para producción.
- `backend`: FastAPI, SQLAlchemy 2, Alembic, PostgreSQL, JWT, Argon2id y
  pytest.

Archivos de referencia:

- [Frontend](frontend/README.md).
- [Backend](backend/README.md).
- [Contexto técnico](CONTEXT.md).

## Cuentas de demostración

El proyecto conserva dos cuentas de demostración para facilitar la evaluación:

| Rol | Correo | Contraseña |
| --- | --- | --- |
| Profesor | `prof@demo.com` | `prof123` |
| Estudiante | `est@demo.com` | `est123` |

Estas cuentas son públicas y se entregan únicamente para pruebas controladas.
No deben usarse para almacenar datos personales, evidencias reales o
información sensible.

## Requisitos

- Docker y Docker Compose.
- Node.js 24.15 o superior compatible con Angular 22.
- pnpm 11.9.
- Python 3.13.
- PostgreSQL accesible para los ambientes requeridos.

Bases de datos previstas:

- `prj_grado_dev`: desarrollo.
- `prj_grado_test`: pruebas automatizadas.
- `prj_grado_prod`: producción.

El usuario de PostgreSQL debe tener permisos para crear y modificar tablas,
índices, restricciones y la tabla de control de Alembic.

## Configuración

Para desarrollo, copia `.env.example` como `.env` y completa las variables
necesarias:

```dotenv
APP_ENV=dev
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:PORT/prj_grado_dev
JWT_SECRET_KEY=replace-with-a-long-random-value
TEACHER_INVITATION_CODE=replace-with-a-private-code
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5.6-luna
CORS_ORIGINS=http://localhost:4200
```

Si la contraseña de PostgreSQL contiene caracteres reservados de URL, debe
codificarse antes de construir `DATABASE_URL`.

`CORS_ORIGINS` acepta uno o varios orígenes separados por comas, sin corchetes
ni comillas JSON:

```dotenv
CORS_ORIGINS=http://localhost:4200,https://lefodigital.example.com
```

El archivo `.env` está excluido de Git y no debe enviarse al repositorio.

## Ejecución con Docker

Desde la raíz del proyecto:

```powershell
docker compose -f docker-compose.dev.yml up --build
```

Servicios locales:

- Angular: `http://localhost:4200`.
- FastAPI: `http://localhost:8000`.
- Swagger en desarrollo: `http://localhost:8000/docs`.

El backend aplica las migraciones con Alembic y ejecuta la semilla idempotente
antes de aceptar solicitudes. El volumen `evidence_dev` conserva las evidencias
aunque los contenedores se reinicien.

Para detener:

```powershell
docker compose -f docker-compose.dev.yml down
```

No uses `-v` si deseas conservar el volumen de evidencias.

## Ejecución nativa

Backend:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
.\.venv\Scripts\alembic.exe upgrade head
.\.venv\Scripts\python.exe -m app.seed
.\.venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
```

Frontend:

```powershell
cd frontend
pnpm install --frozen-lockfile
pnpm start
```

El frontend consume la API mediante la ruta relativa `/api/v1`.

## Migraciones

Aplicar migraciones:

```powershell
cd backend
.\.venv\Scripts\alembic.exe upgrade head
```

Crear una migración después de cambiar modelos:

```powershell
.\.venv\Scripts\alembic.exe revision --autogenerate -m "describe change"
.\.venv\Scripts\alembic.exe check
```

Toda migración debe revisarse antes de aplicarse en una base desplegada.

## Pruebas

Backend:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest
```

Frontend:

```powershell
cd frontend
pnpm test
pnpm run build
```

Validación local más reciente:

- backend: 17 pruebas aprobadas y 94,10 % de cobertura;
- frontend: 36 pruebas aprobadas;
- cobertura frontend superior a los umbrales definidos;
- build Angular de producción aprobado;
- migraciones Alembic aplicadas y sin operaciones pendientes;
- Docker Compose de desarrollo verificado con backend saludable y frontend
  disponible.

## Integración continua

El repositorio incluye un flujo de GitHub Actions en
`.github/workflows/ci.yml`. Este flujo:

- inicia PostgreSQL para pruebas;
- aplica migraciones con Alembic;
- ejecuta pruebas del backend;
- ejecuta pruebas y build del frontend;
- revisa que no se versionen archivos `.env` ni patrones comunes de claves
  privadas;
- publica imágenes privadas en GitLab Container Registry cuando el cambio llega
  a `master` y las credenciales están configuradas en GitHub.

Las imágenes publicadas usan estos nombres lógicos:

```text
registry.gitlab.com/<namespace>/lefodigital/backend:<commit>
registry.gitlab.com/<namespace>/lefodigital/frontend:<commit>
```

También se actualiza la etiqueta `latest` únicamente desde `master`.

## Producción

`docker-compose.prod.yml` no carga archivos `.env`. En producción, las
variables deben inyectarse desde el sistema de despliegue:

- `DATABASE_URL`, apuntando a `prj_grado_prod`.
- `JWT_SECRET_KEY`.
- `TEACHER_INVITATION_CODE`.
- `OPENAI_API_KEY`, opcional si LeFoBot no se habilita.
- `OPENAI_MODEL`, opcional.
- `EVIDENCE_HOST_PATH`, ruta persistente del host.
- `FRONTEND_PORT`, opcional; valor predeterminado `8080`.
- `MAX_UPLOAD_BYTES`, opcional.
- `CHAT_RATE_LIMIT_PER_MINUTE`, opcional.
- `CORS_ORIGINS`, con el origen público autorizado.
- `FORWARDED_ALLOW_IPS`, ajustado al proxy autorizado.

Ejemplo:

```powershell
docker compose -f docker-compose.prod.yml up -d --build
```

La aplicación pública queda expuesta por el contenedor frontend. Nginx sirve
Angular y reenvía `/api` al backend dentro de la red privada de Compose.

## Copias de seguridad y actualización

Antes de actualizar una instalación:

1. Respaldar `prj_grado_prod` con `pg_dump`.
2. Respaldar el volumen de evidencias.
3. Construir o descargar la nueva imagen.
4. Aplicar migraciones una sola vez.
5. Verificar login, actividades, evidencias, reportes y salud del sistema.

PostgreSQL y el volumen de evidencias deben restaurarse como una unidad para
conservar la correspondencia entre metadatos y archivos.

## Seguridad

- La clave OpenAI existe únicamente en FastAPI.
- El historial de LeFoBot no se guarda en PostgreSQL.
- El access JWT permanece solo en memoria del navegador.
- El refresh JWT usa cookie HttpOnly y `Secure` en producción.
- Las descargas de evidencia exigen propiedad o rol docente.
- Las contraseñas usan Argon2id.
- El registro de profesor exige código de invitación.
- OpenAPI se deshabilita cuando `APP_ENV=prod`.
- Los secretos reales no deben copiarse a código, documentación, pruebas,
  imágenes, commits ni archivos de ejemplo.
