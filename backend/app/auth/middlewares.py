import time
import json
import hashlib
import secrets
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from fastapi import Request, Response
from auth import security
from auth.exceptions import LoginRedirectException

logger = logging.getLogger(__name__)

class UserMiddleware(BaseHTTPMiddleware):
    """Middleware para cargar información del usuario en cada request"""

    async def dispatch(self, request: Request, call_next):
        try:
            user = await security.get_current_user_from_cookie(request)
            request.state.user = user
        except Exception as e:
            logger.debug(f"No user found in cookie: {e}")
            request.state.user = None

        response = await call_next(request)
        return response

def get_current_user_from_request(request: Request):
    """Función auxiliar para obtener el usuario del request.state"""
    return getattr(request.state, 'user', None)

def require_authenticated_user(request: Request):
    """Función auxiliar que requiere que el usuario esté autenticado"""
    user = get_current_user_from_request(request)
    if user is None:
        raise LoginRedirectException()
    return user

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware que agrega headers de seguridad robustos"""

    def __init__(self, app, enable_hsts: bool = True, csp_policy: Optional[str] = None):
        super().__init__(app)
        self.enable_hsts = enable_hsts
        self.csp_policy = csp_policy or (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' https:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'"
        )

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Headers de seguridad básicos
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": (
                "geolocation=(), microphone=(), camera=(), "
                "payment=(), usb=(), magnetometer=(), gyroscope=()"
            ),
            "Content-Security-Policy": self.csp_policy,
            "X-Permitted-Cross-Domain-Policies": "none",
            "Cross-Origin-Embedder-Policy": "require-corp",
            "Cross-Origin-Opener-Policy": "same-origin",
            "Cross-Origin-Resource-Policy": "same-origin"
        }

        # HSTS solo en HTTPS
        if self.enable_hsts and request.url.scheme == "https":
            security_headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        # Aplicar headers
        for header, value in security_headers.items():
            response.headers[header] = value

        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware de rate limiting robusto con diferentes límites por endpoint"""

    def __init__(self, app, redis_client=None):
        super().__init__(app)
        self.redis_client = redis_client
        self.memory_store: Dict[str, List[Tuple[float, str]]] = {}

        # Configuración de límites por tipo de endpoint
        self.rate_limits = {
            "/auth/login": {"max_requests": 5, "window_seconds": 300},  # 5 intentos por 5 min
            "/auth/register": {"max_requests": 3, "window_seconds": 3600},  # 3 por hora
            "/auth/password-reset": {"max_requests": 3, "window_seconds": 3600},
            "default": {"max_requests": 100, "window_seconds": 60}  # 100 por minuto general
        }

    def get_client_identifier(self, request: Request) -> str:
        """Obtiene identificador único del cliente"""
        # Priorizar headers de proxy inverso
        forwarded_for = request.headers.get("X-Forwarded-For")
        real_ip = request.headers.get("X-Real-IP")

        if forwarded_for:
            # Tomar la primera IP (cliente original)
            client_ip = forwarded_for.split(",")[0].strip()
        elif real_ip:
            client_ip = real_ip
        else:
            client_ip = request.client.host if request.client else "unknown"

        # Agregar user agent para mejor identificación
        user_agent = request.headers.get("User-Agent", "")
        identifier = f"{client_ip}:{hashlib.sha256(user_agent.encode()).hexdigest()[:8]}"

        return identifier

    def get_rate_limit_config(self, path: str) -> Dict[str, int]:
        """Obtiene configuración de rate limit para un endpoint específico"""
        for endpoint, config in self.rate_limits.items():
            if endpoint != "default" and endpoint in path:
                return config
        return self.rate_limits["default"]

    async def check_rate_limit(self, identifier: str, path: str) -> Tuple[bool, Dict]:
        """Verifica si el cliente excede el rate limit"""
        config = self.get_rate_limit_config(path)
        max_requests = config["max_requests"]
        window_seconds = config["window_seconds"]
        current_time = time.time()

        if self.redis_client:
            # Usar Redis para almacenamiento distribuido
            try:
                key = f"rate_limit:{identifier}:{path}"
                pipe = self.redis_client.pipeline()
                pipe.zremrangebyscore(key, 0, current_time - window_seconds)
                pipe.zcard(key)
                pipe.zadd(key, {str(current_time): current_time})
                pipe.expire(key, window_seconds)
                results = pipe.execute()

                request_count = results[1]

                return request_count < max_requests, {
                    "limit": max_requests,
                    "remaining": max(0, max_requests - request_count - 1),
                    "reset": int(current_time + window_seconds)
                }
            except Exception as e:
                logger.error(f"Redis error in rate limiting: {e}")
                # Fallback a memoria

        # Almacenamiento en memoria (fallback)
        key = f"{identifier}:{path}"

        if key not in self.memory_store:
            self.memory_store[key] = []

        # Limpiar requests antiguos
        self.memory_store[key] = [
            (timestamp, req_path) for timestamp, req_path in self.memory_store[key]
            if current_time - timestamp < window_seconds
        ]

        request_count = len(self.memory_store[key])

        if request_count < max_requests:
            self.memory_store[key].append((current_time, path))
            return True, {
                "limit": max_requests,
                "remaining": max_requests - request_count - 1,
                "reset": int(current_time + window_seconds)
            }

        return False, {
            "limit": max_requests,
            "remaining": 0,
            "reset": int(current_time + window_seconds)
        }

    async def dispatch(self, request: Request, call_next):
        identifier = self.get_client_identifier(request)
        path = str(request.url.path)

        allowed, rate_info = await self.check_rate_limit(identifier, path)

        if not allowed:
            logger.warning(f"Rate limit exceeded for {identifier} on {path}")

            response = JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "detail": "Rate limit exceeded. Please try again later.",
                    "retry_after": rate_info["reset"] - int(time.time())
                }
            )

            # Headers informativos de rate limiting
            response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
            response.headers["X-RateLimit-Remaining"] = str(rate_info["remaining"])
            response.headers["X-RateLimit-Reset"] = str(rate_info["reset"])
            response.headers["Retry-After"] = str(rate_info["reset"] - int(time.time()))

            return response

        response = await call_next(request)

        # Agregar headers de rate limiting a respuestas exitosas
        response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(rate_info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(rate_info["reset"])

        return response

class AuditLogMiddleware(BaseHTTPMiddleware):
    """Middleware mejorado para logging de auditoría con formateo estructurado"""

    def __init__(self, app, log_all_requests: bool = False):
        super().__init__(app)
        self.log_all_requests = log_all_requests

        # Configurar logger específico para auditoría
        self.audit_logger = logging.getLogger("audit")

        # Endpoints sensibles que siempre se loggean
        self.sensitive_paths = {
            "/auth/login", "/auth/logout", "/auth/register",
            "/auth/password-reset", "/auth/change-password",
            "/tasks/delete", "/profile/update", "/admin"
        }

    def is_sensitive_endpoint(self, path: str) -> bool:
        """Verifica si es un endpoint sensible"""
        return any(sensitive in path for sensitive in self.sensitive_paths)

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Información del usuario
        user = getattr(request.state, 'user', None)
        user_info = user.username if user else "anonymous"
        user_id = user.id if user else None

        # Información del cliente
        client_ip = request.headers.get("X-Forwarded-For",
                                       request.headers.get("X-Real-IP",
                                                          request.client.host if request.client else "unknown"))
        user_agent = request.headers.get("User-Agent", "")

        # Información de la petición
        method = request.method
        path = str(request.url.path)
        query_params = str(request.query_params) if request.query_params else ""

        response = await call_next(request)

        # Calcular tiempo de procesamiento
        process_time = time.time() - start_time
        status_code = response.status_code

        # Determinar si debe loggearse
        should_log = (
            self.log_all_requests or
            self.is_sensitive_endpoint(path) or
            status_code >= 400 or
            process_time > 5.0  # Requests lentos
        )

        if should_log:
            # Log estructurado en formato JSON
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": "http_request",
                "method": method,
                "path": path,
                "query_params": query_params,
                "status_code": status_code,
                "process_time": round(process_time, 3),
                "client_ip": client_ip,
                "user_agent": user_agent,
                "user": {
                    "username": user_info,
                    "user_id": user_id
                },
                "sensitive": self.is_sensitive_endpoint(path)
            }

            # Nivel de log según el status code
            if status_code >= 500:
                self.audit_logger.error(json.dumps(log_data))
            elif status_code >= 400:
                self.audit_logger.warning(json.dumps(log_data))
            else:
                self.audit_logger.info(json.dumps(log_data))

        return response

class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """Middleware robusto de protección CSRF con token validation"""

    def __init__(self, app, exempt_paths: Optional[List[str]] = None):
        super().__init__(app)
        self.exempt_paths = exempt_paths or ["/api/auth/token", "/docs", "/openapi.json"]
        self.csrf_tokens: Dict[str, Tuple[str, float]] = {}  # session_id -> (token, timestamp)

    def generate_csrf_token(self) -> str:
        """Genera un token CSRF seguro"""
        return secrets.token_urlsafe(32)

    def is_exempt_path(self, path: str) -> bool:
        """Verifica si el path está exento de protección CSRF"""
        return any(exempt in path for exempt in self.exempt_paths)

    def validate_origin(self, request: Request) -> bool:
        """Valida que el origen del request sea válido"""
        origin = request.headers.get("origin")
        referer = request.headers.get("referer")
        host = request.headers.get("host")

        if not host:
            return False

        allowed_origins = [f"http://{host}", f"https://{host}"]

        # Verificar origen
        if origin and origin not in allowed_origins:
            return False

        # Verificar referer
        if referer and not any(referer.startswith(allowed) for allowed in allowed_origins):
            return False

        return True

    async def dispatch(self, request: Request, call_next):
        path = str(request.url.path)
        method = request.method

        # Saltar protección para endpoints exentos
        if self.is_exempt_path(path):
            return await call_next(request)

        # Solo aplicar a métodos que modifican datos
        if method in ["POST", "PUT", "DELETE", "PATCH"]:

            # Validar origen
            if not self.validate_origin(request):
                logger.warning(f"CSRF: Invalid origin for {path} from {request.client.host}")
                return JSONResponse(
                    status_code=403,
                    content={
                        "error": "CSRF Protection",
                        "detail": "Invalid origin. Cross-site request detected."
                    }
                )

            # Para requests con Content-Type application/json (API calls)
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                # API calls requieren header específico
                csrf_header = request.headers.get("X-Requested-With")
                if csrf_header != "XMLHttpRequest":
                    logger.warning(f"CSRF: Missing X-Requested-With header for API call to {path}")
                    return JSONResponse(
                        status_code=403,
                        content={
                            "error": "CSRF Protection",
                            "detail": "Missing required header for API calls."
                        }
                    )

        return await call_next(request)

class RequestSizeMiddleware(BaseHTTPMiddleware):
    """Middleware para limitar el tamaño de requests"""

    def __init__(self, app, max_size: int = 10 * 1024 * 1024):  # 10MB por defecto
        super().__init__(app)
        self.max_size = max_size

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")

        if content_length:
            try:
                size = int(content_length)
                if size > self.max_size:
                    return JSONResponse(
                        status_code=413,
                        content={
                            "error": "Payload Too Large",
                            "detail": f"Request size {size} exceeds maximum allowed {self.max_size} bytes"
                        }
                    )
            except ValueError:
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "Bad Request",
                        "detail": "Invalid Content-Length header"
                    }
                )

        return await call_next(request)

# Middleware de conveniencia para aplicar todos los middlewares de seguridad
class SecurityMiddlewareStack:
    """Stack completo de middlewares de seguridad"""

    @staticmethod
    def add_security_middlewares(app, redis_client=None, config: Optional[Dict] = None):
        """Agrega todos los middlewares de seguridad a la aplicación"""
        config = config or {}

        # Orden importa: de más específico a más general
        app.add_middleware(RequestSizeMiddleware, max_size=config.get("max_request_size", 10 * 1024 * 1024))
        app.add_middleware(CSRFProtectionMiddleware, exempt_paths=config.get("csrf_exempt_paths"))
        app.add_middleware(AuditLogMiddleware, log_all_requests=config.get("log_all_requests", False))
        app.add_middleware(RateLimitMiddleware, redis_client=redis_client)
        app.add_middleware(SecurityHeadersMiddleware,
                          enable_hsts=config.get("enable_hsts", True),
                          csp_policy=config.get("csp_policy"))
        app.add_middleware(UserMiddleware)