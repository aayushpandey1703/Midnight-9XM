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
            sslrootcert=r"F:\Flask_Projects\Midnight_9XM\DB_cert\ca.pem"
        )
        return True,connection
    except Exception as e:
        logger.error("Error connecting to DB")
        logger.error(str(e))
        return False, None

def create(output):
    cursor=output.cursor()
    query='''
CREATE TABLE "login" (
  id SERIAL PRIMARY KEY,
  username VARCHAR(255) NOT NULL UNIQUE,
  email VARCHAR(255) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL
);

     '''
    cursor.execute(query)
    output.commit()
    cursor.close()
    output.close()
    return

def create_playlist(output):
    cursor=output.cursor()
    query='''
CREATE TABLE "user_playlist" (
  playlist_id SERIAL PRIMARY KEY,
  user_id INT NOT NULL,
  playlist_name varchar(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES login(id) ON DELETE CASCADE
);

     '''
    cursor.execute(query)
    output.commit()
    cursor.close()
    output.close()
    return

def show_table(output):
    cursor=output.cursor()
    query='''   SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public' AND table_type = 'BASE TABLE';'''
    cursor.execute(query)
    table=cursor.fetchall()
    print(table)
    return

def select(output):
    cursor=output.cursor()
    query='''SELECT * FROM login;'''
    cursor.execute(query)
    table=cursor.fetchall()
    print(table)
    return

def select_playlist(output):
    cursor=output.cursor()
    query='''SELECT * FROM user_playlist;'''
    cursor.execute(query)
    table=cursor.fetchall()
    print(table)
    return
status,output=dbconnection()
# create(output)
# # show_table(output)
# select(output)
# create_playlist(output)
select_playlist(output)
