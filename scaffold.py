#!/usr/bin/env python3
"""Bootstrap a minimal microservice repo from templates."""

from __future__ import annotations

import argparse
from pathlib import Path

VALID_TYPES = ("api", "worker")

REPO_ROOT = Path(__file__).resolve().parent
VARIANT_DIRS = frozenset({"api", "worker"})
SKIP_DIRS = frozenset({".git", ".github", *VARIANT_DIRS})
TOOL_FILES = frozenset({"scaffold.py", "README.md", ".gitignore"})
SERVICE_README = "SERVICE_README.md"
GITIGNORE_SERVICE = "gitignore.service"
WORKFLOW_SOURCE = REPO_ROOT / ".github" / "workflows" / "service-ci.yml"


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


def copy_base_templates(dst: Path, mapping: dict[str, str]) -> None:
    readme_src = REPO_ROOT / SERVICE_README
    if not readme_src.is_file():
        raise SystemExit(f"Missing {SERVICE_README} in the scaffolding repo.")
    (dst / "README.md").write_text(
        substitute(readme_src.read_text(encoding="utf-8"), mapping),
        encoding="utf-8",
    )

    gi_src = REPO_ROOT / GITIGNORE_SERVICE
    if not gi_src.is_file():
        raise SystemExit(f"Missing {GITIGNORE_SERVICE} in the scaffolding repo.")
    (dst / ".gitignore").write_text(gi_src.read_text(encoding="utf-8"), encoding="utf-8")

    for path in sorted(REPO_ROOT.iterdir()):
        if path.is_dir():
            if path.name in SKIP_DIRS:
                continue
            copy_tree(path, dst / path.name, mapping)
            continue
        if not path.is_file():
            continue
        if path.name in TOOL_FILES | {SERVICE_README, GITIGNORE_SERVICE}:
            continue
        (dst / path.name).write_text(
            substitute(path.read_text(encoding="utf-8"), mapping),
            encoding="utf-8",
        )


def render_generated_workflow(dst: Path, mapping: dict[str, str]) -> None:
    if not WORKFLOW_SOURCE.is_file():
        raise SystemExit("Missing .github/workflows/service-ci.yml in the scaffolding repo.")
    text = substitute(WORKFLOW_SOURCE.read_text(encoding="utf-8"), mapping)
    out = dst / ".github" / "workflows" / "ci.yml"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")


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

    variant = REPO_ROOT / args.type
    if not variant.is_dir():
        raise SystemExit(
            f"Missing variant folder {args.type!r} (expected {variant})."
        )

    mapping = {
        "__SERVICE_NAME__": args.name,
        "__SERVICE_TYPE__": args.type,
    }

    out.mkdir(parents=True, exist_ok=True)
    copy_base_templates(out, mapping)
    render_generated_workflow(out, mapping)
    copy_tree(variant, out, mapping)

    print(f"Scaffolded service at {out}")
    print("Next: cd", out.name, "&& python -m venv .venv && source .venv/bin/activate")
    print("       pip install -r requirements-dev.txt && pytest && ruff check .")


if __name__ == "__main__":
    main()
