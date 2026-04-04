# storage_service

Scaffold generado con `scaffold.py` (`--type s3`).

## Local

```bash
pip install ruff pytest
ruff check .
pytest -q
docker build -t storage_service:local .
```

## CI

`.github/workflows/deploy.yml`: lint → test → build (imagen local) → push a ECR (OIDC + `vars.AWS_ACCOUNT`, `vars.ENV`).

Imagen: `storage_service-<ENV>:<VERSION>` (lee `VERSION`).

## Terraform

Infra mínima: bucket S3 bajo `terraform/`.

```bash
cd terraform
terraform init
terraform apply
```
