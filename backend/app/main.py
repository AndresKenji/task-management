import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

from auth.router import router as auth_router
from database.database import get_database
from auth.dependencies import AdminUserService

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja el ciclo de vida de la aplicación"""
    # Startup
    logger.info("Iniciando aplicación...")

    try:
        db = get_database()
        logger.info(f"Base de datos inicializada: {db.db_type}")

        if not db.test_connection():
            raise RuntimeError("No se pudo conectar a la base de datos")

        db.create_tables()
        logger.info("Tablas de base de datos creadas/verificadas")

        admin_service = AdminUserService()
        from contextlib import contextmanager

        with contextmanager(db.get_db)() as session:
            admin_user = admin_service.create_or_update_admin_user(session)
            if admin_user:
                logger.info(f"Usuario administrador configurado: {admin_user.username}")
            else:
                logger.warning("No se pudo configurar el usuario administrador")

        logger.info("Aplicación iniciada correctamente")

    except Exception as e:
        logger.error(f"Error durante el inicio: {e}")
        raise

    yield

    logger.info("Cerrando aplicación...")
    try:
        db = get_database()
        db.close()
        logger.info("Conexiones de base de datos cerradas")
    except Exception as e:
        logger.error(f"Error durante el cierre: {e}")

app = FastAPI(
    title="Task Management API",
    description="API para gestión de tareas con autenticación",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(auth_router)

@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado de la aplicación"""
    try:
        db = get_database()
        db_status = db.test_connection()

        return {
            "status": "healthy" if db_status else "unhealthy",
            "database": "connected" if db_status else "disconnected",
            "database_type": db.db_type
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "Task Management API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )