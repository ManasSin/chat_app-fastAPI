import os
from typing import Optional


class Settings:
    def __init__(self):
        # Database Configuration
        self.postgres_url = os.getenv(
            "POSTGRES_URL", "postgresql://user:password@localhost:5432/database"
        )
        self.mongodb_url = os.getenv(
            "MONGODB_URL", "mongodb://localhost:27017/database"
        )

        # Redis Configuration
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

        # Application Configuration
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.environment = os.getenv("ENVIRONMENT", "development")

        # Security
        self.secret_key = os.getenv("SECRET_KEY", "my_secret_key")
        self.algorithm = os.getenv("ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
        )

        # Server Configuration
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8000"))


# Global settings instance
settings = Settings()
