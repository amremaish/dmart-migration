import mysql.connector

from enums import JoinType


class DbManager:
    db_connect = None

    def connect(self) -> bool:
        try:
            self.db_connect = mysql.connector.connect(
                host="127.0.0.1",
                database='zain_test',
                port=3306,
                user="root",
                password="")

        except Exception:
            return False
        return self.db_connect.is_connected()

    def select_query(
            self,
            *,
            table_name: str,
            columns: list,
            join_tables: dict[list, str] | None = None,
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
        sql = ''
        if join_tables:
            for join in join_tables:
                if "table" in join and "pk_id" in join and "fk_id" in join:
                    join_type = JoinType.INNER if "table" not in join else join['join_type']
                    sql += f' {join_type} join {join["table"]} on {join["pk_id"]} = {join["fk_id"]}'
        if limit != -1:
            sql += f' LIMIT {limit} OFFSET {offset}'
        sql += ';'

        # Creating a cursor object using the cursor() method
        cursor = self.db_connect.cursor(buffered=True)

        # Executing the query
        cursor.execute(count_sql + sql)
        count = cursor.fetchone()
        cursor.execute(columns_sql + sql)
        result = cursor.fetchall()
        self.db_connect.commit()

        processed_result: list = []
        # collect result
        for item in result:
            idx = 0
            sub_result: dict = {}
            for col_name in columns:
                sub_result[col_name] = item[idx]
                idx = +1
            processed_result.append(sub_result)
        return {
            'query': columns_sql + sql,
            'data': processed_result,
            'returned': len(processed_result),
            'total': count[0]
        }


db_manager = DbManager()
