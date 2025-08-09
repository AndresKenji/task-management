import os
import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from auth.router import router as auth_router
from task.router import router as task_router
from database.database import get_database,Base
from auth.dependencies import AdminUserService

load_dotenv()

middleware:list[Middleware] = [
    Middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:4200",
                       "http://api:8000",
                       "http://localhost:8000",
                       "http://frontend:80"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    ),
]


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja el ciclo de vida de la aplicación"""
    logger.info("Iniciando aplicación...")

    try:
        time.sleep(2)

        db = get_database()
        logger.info(f"Base de datos inicializada: {db.db_type}")
        logger.info(f"String de conexión: {db.connection_string}")

        # Intentar conectar con reintentos
        max_retries = 5
        for attempt in range(max_retries):
            try:
                if db.test_connection():
                    logger.info("Conexión a base de datos exitosa")
                    break
                else:
                    logger.warning(f"Intento {attempt + 1}/{max_retries} falló")
                    if attempt < max_retries - 1:
                        time.sleep(2)
            except Exception as e:
                logger.error(f"Error en intento {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
        else:
            raise RuntimeError("No se pudo conectar a la base de datos después de múltiples intentos")

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
    lifespan=lifespan,
    middleware=middleware
)

app.include_router(auth_router)
app.include_router(task_router)

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
        reload=False,
        log_level="info"
    )