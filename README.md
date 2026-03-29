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

## Qué genera

| Elemento | Descripción |
|----------|-------------|
| `app/` | Código de la aplicación |
| `Dockerfile` | Imagen lista para construir |
| `.github/workflows/ci.yml` | CI en push a `master` |
| `terraform/` | ECR, bucket S3 cifrado, CloudWatch log group |
| `README.md` | Runbook operacional base en español |

El job `push` reutiliza los mismos pasos que en tu referencia: **Configure AWS credentials** (`configure-aws-credentials@v4`), **Login to AWS ECR** (`amazon-ecr-login@v2`) y el script **Build & Push Docker Image** (tag desde `VERSION`, repo `__SERVICE_NAME__-${{ vars.ENV }}`).

En el repositorio generado debes configurar variables GitHub (`AWS_ACCOUNT`, `ENV`) y el rol OIDC `gh-actions-role` como en tu flujo actual.

## Licencia

Uso libre para proyectos personales o de equipo; ajusta Terraform y permisos IAM a tu organización.
