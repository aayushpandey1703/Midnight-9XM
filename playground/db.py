import psycopg2
from loguru import logger
def dbconnection():
    try:
        connection=psycopg2.connect(
            database="defaultdb",
            host="pg-336977da-aleronpeterson-6630.b.aivencloud.com",
            user="avnadmin",
            password="AVNS_TbvbOoIlAM6X64RKzxL",
            port=19275,
            sslmode="verify-ca",
            sslrootcert="../DB_cert/ca.pem"
        )
        return True,connection
    except Exception as e:
        logger.error("Error connecting to DB")
        logger.error(str(e))
        return False, None

def create(output):
    cursor=output.cursor()
    query='''
CREATE TABLE "User" (
  id SERIAL PRIMARY KEY,
  username VARCHAR(255) NOT NULL UNIQUE,
  email VARCHAR(255) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL
);

     '''
    cursor.execute(query)
    cursor.commit()
    cursor.close()
    output.close()
    return

status,output=dbconnection()
create(output)