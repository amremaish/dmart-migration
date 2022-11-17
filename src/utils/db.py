import mysql.connector


class DbManager:

    def connect(self) -> bool:
        try:
            self.connect = mysql.connector.connect(
                host="127.0.0.1",
                database='zain_test',
                port=3306,
                user="root",
                password="")

        except Exception:
            return False
        return self.connect.is_connected()


db_manager = DbManager()
