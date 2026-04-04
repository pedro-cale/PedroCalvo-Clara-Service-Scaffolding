# Clara Service Scaffolding

CLI mínimo para generar una carpeta lista para ser su propio repositorio (Dockerfile, GitHub Actions, Terraform, README).

## Uso

```bash
chmod +x scaffold.py
./scaffold.py --name storage_service --type s3
./scaffold.py --name config_service --type ssm
```

- **`--name`**: nombre de la carpeta y prefijo; solo `a-z`, `0-9` y `_` (snake_case).
- **`--type`**: `s3` (módulo Terraform con bucket S3) o `ssm` (parámetro SSM de ejemplo).

Se crea `./<name>/` con `Dockerfile`, `app/`, `tests/`, `VERSION`, `.github/workflows/deploy.yml` (lint → test → build → push a ECR) y `terraform/main.tf`.

El job de push reutiliza los pasos de OIDC, login a ECR y build/push del ejemplo Cond-Nast (`configure-aws-credentials`, `amazon-ecr-login`, `docker build/tag/push`). Necesitas `vars.AWS_ACCOUNT` y `vars.ENV` en GitHub.
