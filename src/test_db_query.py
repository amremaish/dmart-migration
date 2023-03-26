import cx_Oracle

from settings import settings

db_host = settings.db_host
db_port = settings.db_port
db_name = settings.db_name
db_user = settings.db_user
db_password = settings.db_password

print(f'Connecting to {db_host} for database `{db_name}`')
connection = cx_Oracle.connect(
    user=db_user,
    password=db_password,
    dsn=f'{db_host}:{db_port}/{db_name}')

print("Connected")
query = "select  DEPARTMENT from USER_ADMIN group by DEPARTMENT"
print("-> Executing: " + query)
cursor = connection.cursor()
cursor.execute(query)
result = cursor.fetchall()
print(result)
