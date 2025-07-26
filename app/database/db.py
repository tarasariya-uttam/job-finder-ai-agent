# Database connection and configuration
# This will handle database setup, connections, and session management

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Placeholder database URL - to be configured via environment variables
DATABASE_URL = "sqlite:///./job_finder.db"

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Only needed for SQLite
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    # Import all models here to ensure they are registered with SQLAlchemy
    # from app.models import models  # Uncomment when models are ready
    
    # Create all tables
    Base.metadata.create_all(bind=engine) 