import os

from dotenv import load_dotenv


class Settings:
    # database connection
    db_host: str = '127.0.0.1'
    db_user: str = 'root'
    db_password: str = ''
    db_port: str = 3306
    db_database: str = 'zain_test'
    database_type = 'oracle'
    fetch_limit = 2

    ORACLE = 'oracle'
    MYSQL = 'mysql'

    def __init__(self):
        load_dotenv("config.env")
        self.MY_ENV_VAR = os.environ.get("MY_ENV_VAR")


settings = Settings()
