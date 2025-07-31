import os
import logging
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from auth.security import get_password_hash, verify_password
from auth.models import User as db_user
from auth import schemas
from database.database import get_database, Database

logger = logging.getLogger(__name__)

class AdminUserService:
    """Servicio para gestionar el usuario administrador"""

    def __init__(self):
        self.admin_username = os.getenv("ADMIN_USERNAME", "administrator")
        self.admin_email = os.getenv("ADMIN_EMAIL", "administrator@dblocal.com")
        self.admin_password = os.getenv("ADMIN_PASSWORD", os.getenv("admin_pwd"))
        self.admin_full_name = os.getenv("ADMIN_FULL_NAME", "administrator local")

    def create_or_update_admin_user(self, db: Session) -> Optional[db_user]:
        """Crea o actualiza el usuario administrador"""
        try:
            logger.info("Checking for admin user in database")

            admin_user = db.query(db_user).filter(
                db_user.username == self.admin_username
            ).first()

            if admin_user is None:
                logger.info(f"Creating new admin user: {self.admin_username}")

                if not self.admin_password:
                    logger.error("Admin password not set in environment variables")
                    raise ValueError("Admin password is required")

                admin_user = db_user(
                    username=self.admin_username,
                    full_name=self.admin_full_name,
                    email=self.admin_email,
                    hashed_password=get_password_hash(self.admin_password),
                    is_admin=True,
                    disabled=False,
                    creation_date=datetime.now(timezone.utc).date()
                )

                db.add(admin_user)
                db.commit()
                db.refresh(admin_user)

                logger.info(f"Admin user created successfully: {self.admin_username}")

            else:
                logger.info("Admin user already exists")

                if self.admin_password and not verify_password(self.admin_password, admin_user.hashed_password):
                    admin_user.hashed_password = get_password_hash(self.admin_password)

                if not admin_user.is_admin:
                    admin_user.is_admin = True
                    logger.warning("Admin user was missing admin privileges - restored")

                if admin_user.disabled:
                    admin_user.disabled = False
                    logger.warning("Admin user was disabled - re-enabled")

                db.commit()
                db.refresh(admin_user)

            return admin_user

        except SQLAlchemyError as e:
            logger.error(f"Database error while managing admin user: {e}")
            db.rollback()
            raise
        except Exception as e:
            logger.error(f"Error managing admin user: {e}")
            db.rollback()
            raise

admin_service: AdminUserService = AdminUserService()

def ensure_admin_user_exists() -> bool:
    """Asegura que el usuario administrador existe"""
    try:
        db: Database = get_database()
        with contextmanager(db.get_db)() as session:
            admin_user: schemas.User | None = admin_service.create_or_update_admin_user(session)
            return admin_user is not None
    except Exception as e:
        logger.error(f"Failed to ensure admin user exists: {e}")
        return False

@asynccontextmanager
async def app_lifespan(app):
    logger.info("Application starting up...")

    try:
        db: Database = get_database()
        if not db.test_connection():
            raise RuntimeError("Database connection failed")

        db.create_tables()

        if not ensure_admin_user_exists():
            raise RuntimeError("Failed to create or verify admin user")

        logger.info("Application startup completed successfully")

    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        raise

    yield

    logger.info("Application shutting down...")
    try:
        db = get_database()
        db.close()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")