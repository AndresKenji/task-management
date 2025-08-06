import logging
from typing import Annotated, List
from datetime import timedelta, datetime

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from auth.schemas import Token, User, UserShow, CreateUser, UserUpdate, ChangePasswordRequest
from auth.models import User as db_user
from database.database import get_database, Database
from auth import security

logger = logging.getLogger(__name__)

database: Database = get_database()

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


@router.post("/token", response_model=Token, summary="Obtener token de acceso")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    request: Request,
    db: Session = Depends(database.get_db)
) -> Token:
    try:
        client_ip = request.headers.get("X-Forwarded-For", request.client.host if request.client else "unknown")
        logger.info(f"Login attempt for user: {form_data.username} from IP: {client_ip}")

        user = security.authenticate_user(form_data.username, form_data.password)
        if not user:
            logger.warning(f"Failed login attempt for user: {form_data.username} from IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if user.disabled:
            logger.warning(f"Login attempt for disabled user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is disabled",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Actualizar último login
        db_user_obj = db.query(db_user).filter(db_user.id == user.id).first()
        if db_user_obj:
            db_user_obj.last_login = datetime.now()
            db.commit()

        access_token_expires: timedelta = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            data={"sub": user.username, "id": user.id},
            expires_delta=access_token_expires
        )

        logger.info(f"Successful login for user: {form_data.username}")
        return Token(access_token=access_token, token_type="bearer")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service temporarily unavailable"
        )

@router.post("/token-cookie", summary="Login con cookie")
async def login_for_access_token_cookie(
    response: Response,
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db)
):

    try:
        client_ip: str = request.headers.get("X-Forwarded-For", request.client.host if request.client else "unknown")
        logger.info(f"Cookie login attempt for user: {form_data.username} from IP: {client_ip}")

        user: User | None = security.authenticate_user(form_data.username, form_data.password)
        if not user or user.disabled:
            logger.warning(f"Failed cookie login for user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials or account disabled"
            )

        # Actualizar último login
        db_user_obj = db.query(db_user).filter(db_user.id == user.id).first()
        if db_user_obj:
            db_user_obj.last_login = datetime.now()
            db.commit()

        access_token_expires: timedelta = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token: str = security.create_access_token(
            data={"sub": user.username, "id": user.id},
            expires_delta=access_token_expires
        )

        security.set_auth_cookie(response, access_token)

        logger.info(f"Successful cookie login for user: {form_data.username}")
        return {"status": "success", "message": "Login successful"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during cookie login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service temporarily unavailable"
        )

@router.post("/logout", summary="Cerrar sesión")
async def logout_user(response: Response):
    security.logout(response)
    return {"status": "success", "message": "Logout successful"}

@router.get("/users/me", response_model=UserShow, summary="Obtener perfil actual")
async def read_users_me(
    current_user: Annotated[User, Depends(security.get_current_active_user)]
) -> UserShow:
    return UserShow.model_validate(current_user)

@router.put("/users/me", response_model=UserShow, summary="Actualizar perfil")
async def update_user_profile(
    user_update: UserUpdate,
    current_user: Annotated[User, Depends(security.get_current_active_user)],
    db: Session = Depends(database.get_db)
) -> UserShow:
    try:
        db_user_obj = db.query(db_user).filter(db_user.id == current_user.id).first()

        if not db_user_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if user_update.email and user_update.email != db_user_obj.email:
            existing_email = db.query(db_user).filter(
                db_user.email == user_update.email,
                db_user.id != current_user.id
            ).first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )

        if user_update.email:
            db_user_obj.email = user_update.email
        if user_update.full_name:
            db_user_obj.full_name = user_update.full_name

        db.commit()
        db.refresh(db_user_obj)

        logger.info(f"User {current_user.username} updated their profile")
        return UserShow.model_validate(db_user_obj)

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error updating user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating profile"
        )

@router.post("/users/me/change-password", summary="Cambiar contraseña")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: Annotated[User, Depends(security.get_current_active_user)],
    db: Session = Depends(database.get_db)
):
    try:
        if not security.verify_password(password_data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        if security.verify_password(password_data.new_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be different from current password"
            )

        db_user_obj = db.query(db_user).filter(db_user.id == current_user.id).first()

        if not db_user_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        db_user_obj.hashed_password = security.get_password_hash(password_data.new_password)
        db.commit()

        logger.info(f"User {current_user.username} changed their password")
        return {"status": "success", "message": "Password changed successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password for user {current_user.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error changing password"
        )

@router.get("/users", response_model=List[UserShow], summary="Listar usuarios (Admin)")
async def list_users(
    current_user: Annotated[User, Depends(security.get_current_admin_user)],
    db: Session = Depends(database.get_db),
    skip: int = 0,
    limit: int = 100
) -> List[UserShow]:
    try:
        users = db.query(db_user).offset(skip).limit(limit).all()
        logger.info(f"Admin {current_user.username} listed users")
        return [UserShow.model_validate(user) for user in users]

    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving users"
        )

@router.post("/users", response_model=UserShow, summary="Crear usuario")
async def create_user(
    user_data: CreateUser,
    #current_user: Annotated[User, Depends(security.get_current_active_user)],
    db: Session = Depends(database.get_db),
):
    try:

        # if current_user:
        #     security.require_admin(current_user)

        existing_username = db.query(db_user).filter(
            db_user.username == user_data.username
        ).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        existing_email = db.query(db_user).filter(
            db_user.email == user_data.email
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        new_user = db_user(
            username=user_data.username,
            full_name=user_data.full_name,
            email=user_data.email,
            hashed_password=security.get_password_hash(user_data.plain_password),
            creation_date=datetime.now().date(),
            disabled=False,
            is_admin=False
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        #creator = current_user.username if current_user else "public"
        logger.info(f"New user created: {user_data.username}")

        return UserShow.model_validate(new_user)

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user"
        )

@router.patch("/users/{user_id}/toggle-status", summary="Habilitar/Deshabilitar usuario (Admin)")
async def toggle_user_status(
    user_id: int,
    current_user: Annotated[User, Depends(security.get_current_admin_user)],
    db: Session = Depends(database.get_db)
):
    try:
        user = db.query(db_user).filter(db_user.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot disable your own account"
            )

        user.disabled = not user.disabled
        user.disable_date = datetime.now().date() if user.disabled else None

        db.commit()

        action = "disabled" if user.disabled else "enabled"
        logger.info(f"Admin {current_user.username} {action} user {user.username}")

        return {
            "status": "success",
            "message": f"User {action} successfully",
            "user": UserShow.model_validate(user)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling user status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user status"
        )

@router.patch("/users/{user_id}/toggle-admin", summary="Otorgar/Quitar permisos admin")
async def toggle_admin_status(
    user_id: int,
    current_user: Annotated[User, Depends(security.get_current_admin_user)],
    db: Session = Depends(database.get_db)
):
    try:
        user = db.query(db_user).filter(db_user.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify your own admin status"
            )

        user.is_admin = not user.is_admin
        db.commit()

        action = "granted" if user.is_admin else "revoked"
        logger.info(f"Admin {current_user.username} {action} admin privileges for user {user.username}")

        return {
            "status": "success",
            "message": f"Admin privileges {action} successfully",
            "user": UserShow.model_validate(user)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling admin status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating admin status"
        )

@router.delete("/users/{user_id}", summary="Eliminar usuario (Admin)")
async def delete_user(
    user_id: int,
    current_user: Annotated[User, Depends(security.get_current_admin_user)],
    db: Session = Depends(database.get_db)
):
    try:
        user = db.query(db_user).filter(db_user.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )

        username = user.username
        db.delete(user)
        db.commit()

        logger.info(f"Admin {current_user.username} deleted user {username}")

        return {
            "status": "success",
            "message": f"User {username} deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting user"
        )