import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # Core settings
    DOWNLOAD_DIR: Path = Path("./downloads")
    MAX_CONCURRENT_DOWNLOADS: int = 4
    DEFAULT_FORMAT: str = "images"
    DELETE_IMAGES_AFTER_CONVERSION: bool = False
    
    # General settings
    CREATE_SUBDIRS: bool = True
    ORGANIZE_BY_DATE: bool = False
    AUTO_CONVERT: bool = False
    
    # Performance settings
    MAX_WORKERS: int = 8
    TIMEOUT: int = 30
    RETRY_ATTEMPTS: int = 3
    CACHE_SIZE: int = 100
    MEMORY_OPTIMIZATION: bool = False
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    RATE_LIMIT: bool = False
    REQUESTS_PER_SEC: int = 5
    
    # Advanced settings
    LOG_LEVEL: str = "INFO"
    FILE_LOGGING: bool = False
    DEBUG_MODE: bool = False
    PDF_QUALITY: str = "High"
    IMAGE_COMPRESSION: int = 85
    PARALLEL_CONVERSION: bool = False
    SMART_RETRY: bool = False
    PREVIEW_MODE: bool = False
    
    HEADERS: dict = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    def __init__(self, **data):
        super().__init__(**data)
        self.DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    def save_to_env(self, env_file: str = '.env'):
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(f"DOWNLOAD_DIR={self.DOWNLOAD_DIR.as_posix()}\n")
            f.write(f"MAX_CONCURRENT_DOWNLOADS={self.MAX_CONCURRENT_DOWNLOADS}\n")
            f.write(f"DEFAULT_FORMAT={self.DEFAULT_FORMAT}\n")
            f.write(f"DELETE_IMAGES_AFTER_CONVERSION={self.DELETE_IMAGES_AFTER_CONVERSION}\n")
            f.write(f"CREATE_SUBDIRS={self.CREATE_SUBDIRS}\n")
            f.write(f"ORGANIZE_BY_DATE={self.ORGANIZE_BY_DATE}\n")
            f.write(f"AUTO_CONVERT={self.AUTO_CONVERT}\n")
            f.write(f"MAX_WORKERS={self.MAX_WORKERS}\n")
            f.write(f"TIMEOUT={self.TIMEOUT}\n")
            f.write(f"RETRY_ATTEMPTS={self.RETRY_ATTEMPTS}\n")
            f.write(f"CACHE_SIZE={self.CACHE_SIZE}\n")
            f.write(f"MEMORY_OPTIMIZATION={self.MEMORY_OPTIMIZATION}\n")
            f.write(f"USER_AGENT={self.USER_AGENT}\n")
            f.write(f"RATE_LIMIT={self.RATE_LIMIT}\n")
            f.write(f"REQUESTS_PER_SEC={self.REQUESTS_PER_SEC}\n")
            f.write(f"LOG_LEVEL={self.LOG_LEVEL}\n")
            f.write(f"FILE_LOGGING={self.FILE_LOGGING}\n")
            f.write(f"DEBUG_MODE={self.DEBUG_MODE}\n")
            f.write(f"PDF_QUALITY={self.PDF_QUALITY}\n")
            f.write(f"IMAGE_COMPRESSION={self.IMAGE_COMPRESSION}\n")
            f.write(f"PARALLEL_CONVERSION={self.PARALLEL_CONVERSION}\n")
            f.write(f"SMART_RETRY={self.SMART_RETRY}\n")
            f.write(f"PREVIEW_MODE={self.PREVIEW_MODE}\n")
            # HEADERS are not typically saved to .env as they are static or derived

# Initialize settings
settings = Settings()
