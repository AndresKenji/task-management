from fastapi import FastAPI
from mangum import Mangum

from identity.interface import router as identity_router
from tickets.interface import router as tickets_router

app = FastAPI(
    title="Task Management API",
    version="0.1.0",
)

app.include_router(tickets_router)
app.include_router(identity_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


handler = Mangum(app)
