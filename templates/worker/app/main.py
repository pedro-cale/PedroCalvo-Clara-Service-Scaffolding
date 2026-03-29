"""Long-running worker entrypoint for __SERVICE_NAME__."""

from __future__ import annotations

import logging
import time

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("__SERVICE_NAME__")


def tick() -> str:
    return "ok"


def main() -> None:
    log.info("worker started for __SERVICE_NAME__")
    while True:
        tick()
        time.sleep(30)


if __name__ == "__main__":
    main()
