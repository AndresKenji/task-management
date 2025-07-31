from typing import Any, Optional, Dict, Generator
import os
from abc import ABC, abstractmethod
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.pool import NullPool, QueuePool
from sqlalchemy import create_engine, Engine, text
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Configuración para diferentes tipos de base de datos"""

    # Configuraciones por defecto para cada tipo de DB
    DEFAULT_CONFIGS = {
        'sqlite': {
            'poolclass': NullPool,
            'connect_args': {"timeout": 15, "check_same_thread": False},
            'echo': False
        },
        'postgresql': {
            'poolclass': QueuePool,
            'pool_size': 10,
            'max_overflow': 20,
            'pool_pre_ping': True,
            'echo': False
        },
        'mysql': {
            'poolclass': QueuePool,
            'pool_size': 10,
            'max_overflow': 20,
            'pool_pre_ping': True,
            'connect_args': {"charset": "utf8mb4"},
            'echo': False
        },
        'mssql': {
            'poolclass': QueuePool,
            'pool_size': 10,
            'max_overflow': 20,
            'pool_pre_ping': True,
            'echo': False
        }
    }

class DatabaseFactory:
    """Factory para crear conexiones de diferentes tipos de base de datos"""

    @staticmethod
    def create_connection_string(db_type: str, **kwargs) -> str:
        """Crea la cadena de conexión según el tipo de base de datos"""

        if db_type.lower() == 'sqlite':
            db_path = kwargs.get('database', './task.db')
            return f"sqlite:///{db_path}"

        elif db_type.lower() == 'postgresql':
            host = kwargs.get('host', 'localhost')
            port = kwargs.get('port', 5432)
            database = kwargs.get('database', 'taskdb')
            username = kwargs.get('username', 'postgres')
            password = kwargs.get('password', '')
            return f"postgresql://{username}:{password}@{host}:{port}/{database}"

        elif db_type.lower() == 'mysql':
            host = kwargs.get('host', 'localhost')
            port = kwargs.get('port', 3306)
            database = kwargs.get('database', 'taskdb')
            username = kwargs.get('username', 'root')
            password = kwargs.get('password', '')
            return f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"

        elif db_type.lower() == 'mssql':
            host = kwargs.get('host', 'localhost')
            port = kwargs.get('port', 1433)
            database = kwargs.get('database', 'taskdb')
            username = kwargs.get('username', 'sa')
            password = kwargs.get('password', '')
            driver = kwargs.get('driver', 'ODBC Driver 17 for SQL Server')
            return f"mssql+pyodbc://{username}:{password}@{host}:{port}/{database}?driver={driver}"

        else:
            raise ValueError(f"Tipo de base de datos no soportado: {db_type}")

class AbstractDatabase(ABC):
    """Clase abstracta para manejo de base de datos"""

    @abstractmethod
    def get_db(self) -> Generator[Session, None, None]:
        """Obtiene una sesión de base de datos"""
        pass

    @abstractmethod
    def get_engine(self) -> Engine:
        """Obtiene el engine de SQLAlchemy"""
        pass

    @abstractmethod
    def close(self) -> None:
        """Cierra las conexiones de la base de datos"""
        pass

class Database(AbstractDatabase):
    def __init__(self, db_type: str | None = None, connection_string: str | None = None, **kwargs) -> None:
        """
        Inicializa la base de datos

        Args:
            db_type: Tipo de base de datos ('sqlite', 'postgresql', 'mysql', 'mssql')
            connection_string: Cadena de conexión personalizada
            **kwargs: Parámetros adicionales para la conexión
        """

        if connection_string is None:
            connection_string = os.getenv("DATABASE_URL") or os.getenv("db_connection")

        if connection_string is None:
            if db_type is None:
                db_type = os.getenv("DB_TYPE", "sqlite")

            # Obtener parámetros desde variables de entorno o kwargs
            db_params: Dict[str, Any] = {
                'host': os.getenv("DB_HOST") or kwargs.get('host'),
                'port': int(os.getenv("DB_PORT")) if os.getenv("DB_PORT") else kwargs.get('port'),
                'database': os.getenv("DB_NAME") or kwargs.get('database'),
                'username': os.getenv("DB_USER") or kwargs.get('username'),
                'password': os.getenv("DB_PASSWORD") or kwargs.get('password'),
            }

            db_params = {k: v for k, v in db_params.items() if v is not None}

            connection_string = DatabaseFactory.create_connection_string(db_type, **db_params)

        if db_type is None:
            db_type = self._detect_db_type(connection_string)

        self.db_type = db_type.lower()
        self.connection_string = connection_string

        # Obtener configuración específica del tipo de DB
        config = DatabaseConfig.DEFAULT_CONFIGS.get(self.db_type, {}).copy()

        # Permitir override de configuración
        engine_config = kwargs.get('engine_config', {})
        config.update(engine_config)

        # Filtrar parámetros válidos para create_engine
        valid_engine_params = {
            'echo', 'echo_pool', 'poolclass', 'pool_size', 'max_overflow',
            'pool_pre_ping', 'pool_recycle', 'pool_timeout', 'connect_args',
            'isolation_level', 'enable_from_linting', 'future'
        }

        filtered_config = {k: v for k, v in config.items() if k in valid_engine_params}

        self.engine = create_engine(
            url=self.connection_string,
            **filtered_config
        )

        # Crear sessionmaker
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

        logger.info(f"Database inicializada: {self.db_type}")

    def _detect_db_type(self, connection_string: str) -> str:
        """Detecta el tipo de base de datos desde la cadena de conexión"""
        if connection_string.startswith('sqlite'):
            return 'sqlite'
        elif connection_string.startswith('postgresql'):
            return 'postgresql'
        elif connection_string.startswith('mysql'):
            return 'mysql'
        elif connection_string.startswith('mssql'):
            return 'mssql'
        else:
            return 'unknown'

    def get_db(self) -> Generator[Session, None, None]:
        """Obtiene una sesión de base de datos"""
        db = self.SessionLocal()
        try:
            yield db
        except Exception as e:
            db.rollback()
            logger.error(f"Error en sesión de DB: {e}")
            raise
        finally:
            db.close()

    def get_engine(self) -> Engine:
        """Obtiene el engine de SQLAlchemy"""
        return self.engine

    def create_tables(self, base_model=None):
        """Crea las tablas en la base de datos"""
        if base_model is None:
            base_model = Base
        base_model.metadata.create_all(bind=self.engine)
        logger.info("Tablas creadas exitosamente")

    def drop_tables(self, base_model=None):
        """Elimina las tablas de la base de datos"""
        if base_model is None:
            base_model = Base
        base_model.metadata.drop_all(bind=self.engine)
        logger.info("Tablas eliminadas exitosamente")

    def test_connection(self) -> bool:
        """Prueba la conexión a la base de datos"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Conexión a la base de datos exitosa")
            return True
        except Exception as e:
            logger.error(f"Error al conectar a la base de datos: {e}")
            return False

    def close(self) -> None:
        """Cierra el engine de la base de datos"""
        if hasattr(self, 'engine'):
            self.engine.dispose()
            logger.info("Conexiones de base de datos cerradas")

    @property
    def conn(self):
        """Propiedad para compatibilidad con código existente"""
        return self.engine.connect()

# Instancia global de la base de datos patron singleton
database_instance: Optional[Database] = None

def get_database() -> Database:
    """Función para obtener la instancia global de la base de datos"""
    global database_instance
    if database_instance is None:
        database_instance = Database()
    return database_instance

def initialize_database(db_type: str, **kwargs) -> Database:
    """Inicializa la base de datos global con configuración específica"""
    global database_instance
    database_instance = Database(db_type=db_type, **kwargs)
    return database_instance

# Base declarativa para los modelos
Base: Any = declarative_base()