import cx_Oracle

from settings import settings

db_host = settings.db_host
db_port = settings.db_port
db_name = settings.db_name
db_user = settings.db_user
db_password = settings.db_password

connection = cx_Oracle.connect(
    user=db_user,
    password=db_password,
    dsn=f'{db_host}:{db_port}/{db_name}')

print(f'Connected to {db_host} for database `{db_name}`')
query = "SELECT count(*) FROM SIM_SWAP LEFT JOIN POS_USER on POS_USER.ID = SIM_SWAP.POS_ID LEFT JOIN LOOKUP on LOOKUP.ID = SIM_SWAP.REASON WHERE REQUEST_TYPE = 'SIM-Swap'"
print("-> Executing: " + query)
cursor = connection.cursor()
cursor.execute(query)
result = cursor.fetchall()
print(result)
