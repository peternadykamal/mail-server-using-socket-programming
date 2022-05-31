from email import message
from re import T
from unittest import result
import mysql.connector
import os


# def storeFileNameInDB(emailID,fileName):
#   dataBase = mysql.connector.connect(
#   host="localhost",
#   user="root",
#   password="",
#   database="mailserverdb"
#   )
#   cursor = dataBase.cursor()
#   query = "INSERT INTO file (email_id, file_name) VALUES (%s,%s);"
#   attributes = (emailID, fileName)
#   try:
#     cursor.execute(query,attributes)
#   except Exception as e: 
#     dataBase.close()
#     return False
#   dataBase.commit()
#   dataBase.close()
#   return True

# storeFileNameInDB(10,"hello.pdf")
print(os.path.basename("/peternady@computerdep.eg/8/test.pdf"))