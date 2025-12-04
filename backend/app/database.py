from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import event
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./catchthediff.db"
    DEBUG: bool = False
    ALLOWED_ORIGINS: str = "http://localhost:5173"

    class Config:
        env_file = ".env"

settings = Settings()

engine = create_async_engine(
    settings.DATABASE_URL, 
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={
        "timeout": 30
    }
)

# Enable WAL mode for better concurrency
@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    # WAL mode allows multiple readers even during writes
    cursor.execute("PRAGMA journal_mode=WAL")
    # Increase cache size to 64MB
    cursor.execute("PRAGMA cache_size=-64000")
    # Use memory for temp storage
    cursor.execute("PRAGMA temp_store=MEMORY")
    # Reduce synchronous for better performance (still safe with WAL)
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
