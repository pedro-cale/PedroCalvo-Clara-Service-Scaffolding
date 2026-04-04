#!/usr/bin/env python3
"""Genera una carpeta con Dockerfile, GHA deploy, Terraform y README."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

VALID_TYPES = ("s3", "ssm")


def die(msg: str) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def safe_name(name: str) -> None:
    if not re.fullmatch(r"[a-z][a-z0-9_]*", name):
        die("Usa --name en snake_case (ej. storage_service), solo minúsculas, números y _.")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def terraform_s3(service: str) -> str:
    return '''terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  type    = string
  default = "us-west-2"
}

variable "service_name" {
  type    = string
  default = "__SVC__"
}

resource "aws_s3_bucket" "data" {
  bucket_prefix = "${var.service_name}-"
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "data" {
  bucket                  = aws_s3_bucket.data.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
'''.replace("__SVC__", service)


def terraform_ssm(service: str) -> str:
    return '''terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  type    = string
  default = "us-west-2"
}

variable "service_name" {
  type    = string
  default = "__SVC__"
}

resource "aws_ssm_parameter" "placeholder" {
  name  = "/${var.service_name}/placeholder"
  type  = "String"
  value = "change-me"
}
'''.replace("__SVC__", service)


def deploy_yml(service: str) -> str:
    # Build/push alineados con Cond-Nast: VERSION, OIDC, ECR, docker build/tag/push.
    return f"""name: Deploy

on:
  push:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install ruff
      - run: ruff check .

  test:
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install pytest
      - run: pytest -q

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t {service}:ci .

  push:
    needs: build
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v3

      - name: Read version
        id: version
        run: |
          VERSION=$(cat VERSION)
          echo "version=$VERSION" >> $GITHUB_OUTPUT

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::${{{{ vars.AWS_ACCOUNT }}}}:role/gh-actions-role
          aws-region: us-west-2

      - name: Login to AWS ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build & Push Docker Image
        id: build-image
        run: |
          VERSION=${{{{ steps.version.outputs.version }}}}
          ECR_REPO={service}-${{{{ vars.ENV }}}}

          docker build -t $ECR_REPO:$VERSION .
          docker tag $ECR_REPO:$VERSION ${{{{ steps.login-ecr.outputs.registry }}}}/$ECR_REPO:$VERSION
          docker push ${{{{ steps.login-ecr.outputs.registry }}}}/$ECR_REPO:$VERSION

          echo "image_tag=$VERSION" >> $GITHUB_OUTPUT
"""


def service_readme(service: str, kind: str) -> str:
    infra = "bucket S3" if kind == "s3" else "parámetro SSM de ejemplo"
    return f"""# {service}

Scaffold generado con `scaffold.py` (`--type {kind}`).

## Local

```bash
pip install ruff pytest
ruff check .
pytest -q
docker build -t {service}:local .
```

## CI

`.github/workflows/deploy.yml`: lint → test → build (imagen local) → push a ECR (OIDC + `vars.AWS_ACCOUNT`, `vars.ENV`).

Imagen: `{service}-<ENV>:<VERSION>` (lee `VERSION`).

## Terraform

Infra mínima: {infra} bajo `terraform/`.

```bash
cd terraform
terraform init
terraform apply
```
"""


def main() -> None:
    p = argparse.ArgumentParser(description="Scaffold mínimo: storage S3 o parámetros SSM.")
    p.add_argument("--name", required=True, help="Nombre de carpeta y prefijo (snake_case).")
    p.add_argument("--type", choices=VALID_TYPES, required=True, help="s3 | ssm")
    args = p.parse_args()

    safe_name(args.name)
    root = Path(args.name).resolve()
    if root.exists():
        die(f"Ya existe: {root}")

    svc = args.name
    tf = terraform_s3(svc) if args.type == "s3" else terraform_ssm(svc)

    write(root / "Dockerfile", "FROM python:3.12-slim\nWORKDIR /app\nCOPY app ./app\nCMD [\"python\", \"-c\", \"print('ok')\"]\n")
    write(root / "VERSION", "0.1.0\n")
    write(root / "app" / "__init__.py", "")
    write(root / "app" / "main.py", 'def ok() -> bool:\n    return True\n')
    write(root / "tests" / "test_main.py", "from app.main import ok\n\ndef test_ok():\n    assert ok()\n")
    write(
        root / "pyproject.toml",
        '[tool.ruff]\nline-length = 100\ntarget-version = "py312"\n\n'
        '[tool.pytest.ini_options]\npythonpath = ["."]\n',
    )
    write(root / ".gitignore", ".venv/\n__pycache__/\n.pytest_cache/\n.terraform/\n*.tfstate*\n")
    write(root / "terraform" / "main.tf", tf)
    write(root / ".github" / "workflows" / "deploy.yml", deploy_yml(svc))
    write(root / "README.md", service_readme(svc, args.type))

    print(f"Listo: {root}")


if __name__ == "__main__":
    main()
