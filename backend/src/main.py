from fastapi import FastAPI
from mangum import Mangum

app = FastAPI(
    title="Task Management API",
    version="0.1.0",
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


handler = Mangum(app)
