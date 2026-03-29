#!/usr/bin/env python3
"""Bootstrap a minimal microservice repo from templates."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

VALID_TYPES = ("api", "worker")

TEMPLATE_ROOT = Path(__file__).resolve().parent / "templates"


def substitute(text: str, mapping: dict[str, str]) -> str:
    for key, value in mapping.items():
        text = text.replace(key, value)
    return text


def copy_tree(src: Path, dst: Path, mapping: dict[str, str]) -> None:
    for path in sorted(src.rglob("*")):
        if path.is_dir():
            continue
        rel = path.relative_to(src)
        out = dst / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        raw = path.read_text(encoding="utf-8")
        out.write_text(substitute(raw, mapping), encoding="utf-8")


def validate_service_name(name: str) -> None:
    if not name or not name.replace("-", "").replace("_", "").isalnum():
        raise SystemExit(
            "Invalid --name: use letters, numbers, hyphens and underscores only "
            "(e.g. payments-service)."
        )
    if name != name.lower():
        raise SystemExit("--name should be lowercase for Docker/ECR/S3 consistency.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scaffold a minimal Python microservice with Docker, CI, and Terraform."
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Service name (e.g. payments-service). Used for image, bucket prefix, docs.",
    )
    parser.add_argument(
        "--type",
        choices=VALID_TYPES,
        required=True,
        help="api: FastAPI + uvicorn. worker: long-running process entrypoint.",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Output directory (default: ./<name>).",
    )
    args = parser.parse_args()

    validate_service_name(args.name)

    out = Path(args.out or args.name).resolve()
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"Refusing to write into non-empty directory: {out}")

    common = TEMPLATE_ROOT / "common"
    variant = TEMPLATE_ROOT / args.type
    if not common.is_dir() or not variant.is_dir():
        raise SystemExit("Template folders are missing; reinstall the scaffolding repo.")

    mapping = {
        "__SERVICE_NAME__": args.name,
        "__SERVICE_TYPE__": args.type,
    }

    out.mkdir(parents=True, exist_ok=True)
    copy_tree(common, out, mapping)
    copy_tree(variant, out, mapping)

    print(f"Scaffolded service at {out}")
    print("Next: cd", out.name, "&& python -m venv .venv && source .venv/bin/activate")
    print("       pip install -r requirements-dev.txt && pytest && ruff check .")


if __name__ == "__main__":
    main()
