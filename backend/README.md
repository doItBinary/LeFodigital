# Backend de LeFodigital

API FastAPI modular con SQLAlchemy 2, Alembic, JWT y PostgreSQL.

La configuración completa, Docker, migraciones, pruebas y despliegue en
TrueNAS se documentan en el [README raíz](../README.md). Las decisiones
técnicas están en [CONTEXT.md](../CONTEXT.md) y las reglas de mantenimiento en
[AGENTS.md](../AGENTS.md).

## Desarrollo nativo

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
.\.venv\Scripts\alembic.exe upgrade head
.\.venv\Scripts\python.exe -m app.seed
.\.venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
```

El archivo `.env` solo se carga con `APP_ENV=dev` y nunca debe versionarse.

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\alembic.exe upgrade head --sql
```

La comprobación completa de divergencias requiere una instancia PostgreSQL:

```powershell
.\.venv\Scripts\alembic.exe check
```
