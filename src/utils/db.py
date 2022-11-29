from datetime import datetime

import cx_Oracle
import mysql.connector

from enums import DBType
from enums import JoinType
from settings import settings


class DbManager:
    # connection  

    def connect(self) -> bool:
        if settings.db_driver == DBType.MYSQL:
            try:
                self.connection = mysql.connector.connect(
                    host=settings.db_host,
                    database=settings.db_name,
                    port=settings.db_port,
                    user=settings.db_user,
                    password=settings.db_password)

            except Exception as ex:
                print(ex)
                return False

            return self.connection.is_connected()
        elif settings.db_driver == DBType.ORACLE:
            try:
                self.connection = cx_Oracle.connect(
                    user=settings.db_user,
                    password=settings.db_password,
                    dsn=f'{settings.db_host}:{settings.db_port}/{settings.db_name}')

            except Exception as ex:
                print(ex)
                return False
            return True
        else:
            raise Exception("Not specified database driver")

    def select_query(
            self,
            *,
            table_name: str,
            columns: list,
            join_tables: dict | None = None,
            limit: int = -1,
            offset: int = 0
    ):
        # columns example
        # data = ["id", "name", "age"]
        # join_tables example
        # join_tables = [
        #     {
        #         "table": "DETAILS",
        #         "pk_id": "POS_USER.ID",
        #         "fk_id": "DETAILS.POS_USER_ID",
        #         "join_type": JoinType.INNER
        #     }
        # ]
        columns_sql = f'SELECT {" ,".join(columns)} FROM {table_name}'
        count_sql = f'SELECT count(*) FROM {table_name}'
        limit_sql = ''
        sql = ''
        if join_tables:
            for join in join_tables:
                if "table" in join and "pk_id" in join and "fk_id" in join:
                    join_type = JoinType.INNER if "table" not in join else join['join_type']
                    sql += f' {join_type} JOIN {join["table"]} on {join["pk_id"]} = {join["fk_id"]}'

        result = None
        count = (0, 0)

        if settings.db_driver == DBType.MYSQL:
            if limit != -1:
                limit_sql = f' LIMIT {limit} OFFSET {offset};'
            else:
                sql += ';'
            # Creating a cursor object using the cursor() method
            cursor = self.connection.cursor(buffered=True)
            # Executing the query
            cursor.execute(count_sql + sql)
            count = cursor.fetchone()
            cursor.execute(columns_sql + sql + limit_sql)
            result = cursor.fetchall()
            self.connection.commit()
        elif settings.db_driver == DBType.ORACLE:

            if limit != -1:
                limit_sql = f" OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY"
            cursor = self.connection.cursor()
            print("-> Processing count: " + count_sql + sql)
            cursor.execute(count_sql + sql)
            count = cursor.fetchone()
            print("-> count executed.")
            print(f"-> Processing: {columns_sql}{sql}{limit_sql}")
            cursor.execute(f'{columns_sql}{sql}{limit_sql}')
            result = cursor.fetchall()
            print("-> query executed.")

        processed_result: list = []
        # collect result
        for item in result:
            idx = 0
            sub_result: dict = {}
            for col_name in columns:
                val = item[idx]
                if type(val) == datetime:
                    val = item[idx].isoformat()
                sub_result[col_name] = val
                idx = idx + 1
            processed_result.append(sub_result)
        return {
            'query': columns_sql + sql + limit_sql,
            'data': processed_result,
            'returned': len(processed_result),
            'total': count[0],
            'offset': offset
        }

    def find_in_row(self, row: dict, key: str):
        key = key.upper()
        key = self.create_alias(key)
        return row.get(key)

    def create_aliases(self, cols):
        return [self.create_alias(col) for col in cols]

    def create_alias(self, col_name: str):
        prefix = col_name.split(".")[0]
        postfix = col_name.split(".")[1]
        if len(prefix) > 4:
            prefix = prefix[:4]
        return f'{col_name} {prefix}_{postfix}_'


db_manager = DbManager()
