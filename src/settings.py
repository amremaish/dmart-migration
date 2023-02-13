import os

# from dotenv import load_dotenv
from pydantic import BaseSettings  # BaseModel,

from enums import DBType


class Settings(BaseSettings):
    db_host: str = '10.50.9.106'
    db_user: str = 'tele'
    db_password: str = 'tele123'
    db_port: str = "1526"
    db_name: str = 'mobtst'
    fetch_limit = 10
    max_records = 1000
    db_driver: str = DBType.ORACLE

    class Config:
        env_file = os.getenv("BACKEND_ENV", "config.env")
        env_file_encoding = "utf-8"


settings = Settings()
