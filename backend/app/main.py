from fastapi import FastAPI

app = FastAPI(title="Suggestor")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
