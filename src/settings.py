import os

from dotenv import load_dotenv


class Settings:
    # database connection
    db_host: str
    db_port: str
    db_password: str

    def __init__(self):
        load_dotenv("config.env")
        self.MY_ENV_VAR = os.environ.get("MY_ENV_VAR")
        print(self.MY_ENV_VAR)


settings = Settings()
