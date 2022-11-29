import os

# from dotenv import load_dotenv
from pydantic import BaseSettings  # BaseModel,

from enums import DBType


class Settings(BaseSettings):
    db_host: str = '127.0.0.1'
    db_user: str = 'root'
    db_password: str = ''
    db_port: str = "3306"
    db_name: str = 'zain_test'
    fetch_limit = 500
    max_records = 2000
    db_driver: str = DBType.ORACLE

    class Config:
        env_file = os.getenv("BACKEND_ENV", "config.env")
        env_file_encoding = "utf-8"


settings = Settings()
