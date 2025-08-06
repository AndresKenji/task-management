from contextlib import contextmanager
import os
import jwt
import logging
from typing import Annotated, Optional, Any
from jwt.exceptions import InvalidTokenError, PyJWTError
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Depends, status, Request, Response
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from auth import models, schemas
from auth.exceptions import LoginRedirectException
from database.database import Database, get_database

logger = logging.getLogger(__name__)

# Configuración
SECRET_KEY: str | None = os.getenv('SECRET_KEY')
ALGORITHM: str = os.getenv('ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))

# Validaciones de configuración
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required")

pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="/api/auth/token", auto_error=False)

class SecurityError(HTTPException):
    """Base exception for security-related errors"""
    pass

class AuthenticationError(SecurityError):
    """Authentication failed"""
    def __init__(self, detail: str = "Could not validate credentials") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

class AuthorizationError(SecurityError):
    """Authorization failed"""
    def __init__(self, detail: str = "Insufficient permissions") -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )



# Funciones de utilidad para passwords
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña coincide con el hash"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False

def get_password_hash(password: str) -> str:
    """Genera hash de la contraseña"""
    return pwd_context.hash(password)

# Funciones de base de datos
def get_user_by_username(username: str) -> Optional[schemas.User]:
    """Obtiene usuario por nombre de usuario"""
    try:
        db: Database = get_database()
        with contextmanager(db.get_db)() as session:
            user: models.User = session.query(models.User).filter(
                models.User.username == username
            ).first()

            if user:
                return schemas.User.model_validate(user)
            return None
    except Exception as e:
        logger.error(f"Error getting user {username}: {e}")
        return None

def get_user_by_id(user_id: int) -> Optional[schemas.User]:
    """Obtiene usuario por ID"""
    try:
        db: Database = get_database()
        with contextmanager(db.get_db)() as session:
            user: models.User = session.query(models.User).filter(
                models.User.id == user_id
            ).first()

            if user:
                return schemas.User.model_validate(user)
            return None
    except Exception as e:
        logger.error(f"Error getting user by ID {user_id}: {e}")
        return None

# Autenticación
def authenticate_user(username: str, password: str) -> Optional[schemas.User]:
    """Autentica usuario con credenciales"""
    user = get_user_by_username(username)
    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user

# Manejo de tokens JWT
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea token de acceso JWT"""
    to_encode = data.copy()

    if expires_delta:
        expire: datetime = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    try:
        encoded_jwt: str = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating access token: {e}")
        raise SecurityError(status_code=500, detail="Error creating token")

def decode_token(token: str) -> dict:
    """Decodifica y valida token JWT"""
    try:
        payload: Any = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token")
    except Exception as e:
        logger.error(f"Error decoding token: {e}")
        raise AuthenticationError("Token validation failed")

# Funciones para obtener usuario actual
async def get_current_user(token: Annotated[Optional[str], Depends(oauth2_scheme)]) -> schemas.User:
    """Obtiene usuario actual desde token Bearer"""
    if not token:
        raise AuthenticationError()

    payload = decode_token(token)
    username: str = payload.get("sub")

    if not username:
        raise AuthenticationError("Invalid token payload")

    user = get_user_by_username(username)
    if not user:
        raise AuthenticationError("User not found")

    return user

async def get_current_user_from_cookie(request: Request) -> Optional[schemas.User]:
    """Obtiene usuario actual desde cookie (para web)"""
    try:
        token: str | None = request.cookies.get("access_token")
        if not token:
            return None

        payload = decode_token(token)
        username: str = payload.get("sub")
        user_id: int = payload.get("id")

        if not username or not user_id:
            return None

        user: schemas.User | None = get_user_by_username(username)
        if not user or user.id != user_id:
            return None

        return user

    except (PyJWTError, AuthenticationError):
        # Log pero no lanzar excepción para cookies
        logger.warning("Invalid token in cookie")
        return None
    except Exception as e:
        logger.error(f"Error getting user from cookie: {e}")
        return None

async def get_current_active_user(current_user: Annotated[schemas.User, Depends(get_current_user)]) -> schemas.User:
    """Obtiene usuario actual y verifica que esté activo"""
    if current_user.disabled:
        raise AuthorizationError("User account is disabled")
    return current_user

# Funciones de autorización
def require_admin(user: schemas.User) -> None:
    """Verifica que el usuario sea administrador"""
    if not user.is_admin:
        raise AuthorizationError("Administrator privileges required")

async def get_current_admin_user(current_user: Annotated[schemas.User, Depends(get_current_active_user)]) -> schemas.User:
    """Dependency que requiere usuario administrador"""
    require_admin(current_user)
    return current_user

# Funciones de login/logout
async def require_login(request: Request) -> schemas.User:
    """
    Dependency que requiere usuario logueado (para web).
    Lanza LoginRedirectException si no está autenticado.
    """
    user = await get_current_user_from_cookie(request)
    if user is None:
        raise LoginRedirectException()

    if user.disabled:
        raise LoginRedirectException()

    return user

def logout(response: Response) -> None:
    """
    Logout user eliminando la cookie
    """
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=True,  # HTTPS en producción
        samesite="strict"
    )

def set_auth_cookie(response: Response, token: str) -> None:
    """
    Establece cookie de autenticación de forma segura
    """
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,  # HTTPS en producción
        samesite="strict",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

# Dependencies reutilizables
CurrentUser: type[schemas.User] = Annotated[schemas.User, Depends(get_current_user)]
CurrentActiveUser: type[schemas.User] = Annotated[schemas.User, Depends(get_current_active_user)]
CurrentAdminUser: type[schemas.User] = Annotated[schemas.User, Depends(get_current_admin_user)]
RequiredLogin: type[schemas.User] = Annotated[schemas.User, Depends(require_login)]