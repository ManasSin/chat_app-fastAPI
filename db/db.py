from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from models.models import Base
import pymongo
from pymongo import MongoClient
from core.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# PostgreSQL connection with connection pooling
engine = create_engine(
    settings.postgres_url,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.debug,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# MongoDB connection
try:
    mongo_client = MongoClient(
        settings.mongodb_url,
        serverSelectionTimeoutMS=5000,
        maxPoolSize=50,
        minPoolSize=10,
    )
    # Test the connection
    mongo_client.admin.command("ping")
    mongo_db = mongo_client["database"]
    logger.info("MongoDB connection established successfully")
except Exception as e:
    #  pylint: disable=logging-fstring-interpolation
    logger.error(f"Failed to connect to MongoDB: {e}")
    mongo_db = None


def get_db():
    """Get database session with proper error handling"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_mongo_client():
    """Get MongoDB database instance"""
    return mongo_db


def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        #  pylint: disable=logging-fstring-interpolation
        logger.error(f"Failed to create database tables: {e}")
        raise
