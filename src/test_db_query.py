import cx_Oracle

db_host = '10.50.9.106'
db_port = '1526'
db_name = 'mobtst'
db_user = 'tele'
db_password = 'tele123'

connection = cx_Oracle.connect(
    user=db_user,
    password=db_password,
    dsn=f'{db_host}:{db_port}/{db_name}')

query = "SELECT DISTRIBUTORS.NAME ,DISTRIBUTORS.MSISDN ,DISTRIBUTORS.STATUS ,DISTRIBUTORS.CREATION_DATE ,DISTRIBUTORS.UPDATED_DATE ,DISTRIBUTORS.PASSWORD ,DISTRIBUTORS.NAME_AR ,DISTRIBUTORS.NAME_KU ,DISTRIBUTORS.LANGUAGE_ID ,REGION.NAME_AR ,REGION.NAME_EN ,REGION.NAME_KU FROM DISTRIBUTORS INNER JOIN DISTRIBUTOR_REGION on DISTRIBUTORS.ID = DISTRIBUTOR_REGION.DISTRIBUTOR_ID INNER join REGION on REGION.ID = DISTRIBUTOR_REGION.REGION_ID OFFSET 0 ROWS FETCH NEXT 500 ROWS ONLY"
print("-> Processing: " + query)
cursor = connection.cursor()
cursor.execute(query)
result = cursor.fetchall()
print("")
print(result)
