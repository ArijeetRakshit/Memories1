from mysql.connector import(
    connect,
    Error,
    errorcode
)

from dotenv import load_dotenv
import os

def create_db_connection():
    load_dotenv("variables.env")
    ctx = None

    try:
        ctx = connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DATABASE')
        )
        print("Connection established successfully")
        return ctx

    except Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database doesnot exist")
        else:
            print(err)
        raise Exception('Some error occured')