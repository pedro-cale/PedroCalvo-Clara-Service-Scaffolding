# __SERVICE_NAME__

Microservicio generado con Clara Service Scaffolding (`__SERVICE_TYPE__`).

## Desarrollo local

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
ruff check . && ruff format --check .
pytest -q
```

### Contenedor

```bash
docker build -t __SERVICE_NAME__:local .
docker run --rm -p 8080:8080 __SERVICE_NAME__:local
```

> **Worker:** el servicio no expone HTTP; omite `-p` y revisa logs con `docker run --rm __SERVICE_NAME__:local`.

## Versionado

El archivo `VERSION` define la etiqueta de imagen que publica CI. Incrementa semver antes de releases.

## CI/CD (GitHub Actions)

El workflow `.github/workflows/ci.yml` corre en cada push a `master`:

1. **lint** — `ruff check` y `ruff format --check`
2. **test** — `pytest`
3. **build** — valida `docker build`
4. **push** — asume rol OIDC en AWS, login a ECR y publica la imagen

### Requisitos en GitHub

- Variables de repositorio (o entorno): `AWS_ACCOUNT`, `ENV` (debe coincidir con el sufijo del repositorio ECR, p. ej. `dev`).
- Rol IAM `gh-actions-role` en la cuenta `AWS_ACCOUNT` con permisos ECR (y los que necesite tu org).
- **Settings → Actions → General:** permitir OIDC si aplica.

La imagen se etiqueta como `__SERVICE_NAME__-<ENV>:<VERSION>` (mismo patrón que `ECR_REPO` en el job `push`).

## Infraestructura (Terraform)

Módulo mínimo bajo `terraform/`:

- Repositorio **ECR** (`<service>-<environment>`)
- **S3** con cifrado SSE-S3 y bloqueo de acceso público
- **CloudWatch log group** reservado para runtime

### Uso rápido

```bash
cd terraform
terraform init
terraform plan -var="service_name=__SERVICE_NAME__" -var="environment=dev"
terraform apply -var="service_name=__SERVICE_NAME__" -var="environment=dev"
```

Ajusta backend remoto y políticas IAM según tu plataforma (ECS, EKS, Lambda, etc.).

---

## Runbook operacional

### Qué es este servicio

- **Nombre:** `__SERVICE_NAME__`
- **Tipo:** `__SERVICE_TYPE__` (API HTTP o proceso worker)
- **Imagen:** ECR en la cuenta configurada en CI; tag = contenido de `VERSION`

### Salud y comprobaciones

| Comprobación | Acción |
|--------------|--------|
| API viva | `GET /health` debe responder `200` y `{"status":"ok",...}` |
| Worker | Proceso en ejecución; logs en CloudWatch (grupo `/microservices/__SERVICE_NAME__-<env>` tras despliegue) |
| Colas / deps | Documentar aquí integraciones reales al evolucionar el servicio |

### Despliegue

1. Merge a `master` tras revisión.
2. Verificar workflow **CI** en GitHub (lint → test → build → push).
3. Confirmar imagen nueva en ECR con el tag de `VERSION`.
4. Aplicar cambios de infra con Terraform si hubo cambios en `terraform/`.

### Rollback

1. Identificar tag de imagen estable anterior en ECR.
2. Redeploy del workload (ECS/K8s/etc.) apuntando a ese tag.
3. Si el fallo es de datos, coordinar con el bucket S3 (`terraform output s3_bucket_id`).

### Incidentes

1. Revisar logs en CloudWatch para el log group del servicio.
2. Confirmar cuotas y errores en ECR/S3 en la consola AWS.
3. Escalar según proceso interno de la organización.

### Contacto / ownership

Completar: equipo responsable, canal de alertas (PagerDuty, Slack, etc.).
