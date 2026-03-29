from fastapi import FastAPI

app = FastAPI(title="__SERVICE_NAME__", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "__SERVICE_NAME__"}
