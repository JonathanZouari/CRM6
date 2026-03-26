import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")


class Config:
    DATABASE_URL = os.environ.get("DATABASE_URL", "")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*").split(",")

    @classmethod
    def reload(cls):
        load_dotenv(Path(__file__).parent / ".env", override=True)
        cls.DATABASE_URL = os.environ.get("DATABASE_URL", "")
        cls.OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
        cls.ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*").split(",")

    @classmethod
    def validate(cls):
        if not cls.DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is required")
