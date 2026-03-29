# Clara Service Scaffolding

Herramienta mínima en Python para generar el esqueleto de un microservicio: aplicación Python, `Dockerfile`, GitHub Actions (lint, test, build, push a ECR) y Terraform (ECR, S3, log group en CloudWatch).

## Uso

```bash
chmod +x scaffold.py
./scaffold.py --name payments-service --type api
```

Tipos soportados:

- `api` — FastAPI + Uvicorn, endpoint `GET /health`
- `worker` — proceso largo con bucle simple (ampliable)

Por defecto se crea un directorio con el mismo nombre que `--name`. Para otra ruta:

```bash
./scaffold.py --name orders-worker --type worker --out ./mis-repos/orders-worker
```

Requisitos: Python 3.10+ (solo biblioteca estándar).

## Estructura de este repositorio

| Ruta | Rol |
|------|-----|
| `scaffold.py` | CLI: copia archivos de la raíz (menos `api/` / `worker/`), sustituye placeholders y escribe `.github/workflows/ci.yml` en el destino. |
| `.github/workflows/service-ci.yml` | Plantilla del CI del microservicio; `scaffold.py` genera `ci.yml` en el destino. Los `paths` del push excluyen `pyproject.toml` y `requirements-dev.txt` de la raíz del scaffolding para no disparar el job aquí; incluye `workflow_dispatch`. |
| `SERVICE_README.md` | README del servicio (placeholders); en el destino pasa a ser `README.md`. |
| `gitignore.service` | Contenido de `.gitignore` del servicio generado. |
| `VERSION`, `requirements-dev.txt`, `pyproject.toml`, `terraform/` | Plantillas base copiadas al servicio. |
| `api/`, `worker/` | Variantes; se copia una según `--type`. |

## Qué genera el scaffold

| Elemento | Descripción |
|----------|-------------|
| `app/` | Código (desde `api/` o `worker/`) |
| `Dockerfile` | Imagen lista para construir |
| `.github/workflows/ci.yml` | CI en push a `main` o `master` (con filtros de rutas) |
| `terraform/` | ECR, bucket S3 cifrado, CloudWatch log group |
| `README.md` | Runbook (desde `SERVICE_README.md`) |

El job `push` reutiliza **Configure AWS credentials**, **Login to AWS ECR** y **Build & Push Docker Image** como en tu referencia.

## Licencia

Uso libre para proyectos personales o de equipo; ajusta Terraform y permisos IAM a tu organización.
