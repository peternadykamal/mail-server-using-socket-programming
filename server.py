from concurrent.futures import thread
from operator import truediv
import socket
import threading
import time
import pickle
import mysql.connector
import os
from pathlib import Path

BUFFER_SIZE = 4096
header = 64 #in bytes
port = 5050
serverIP = socket.gethostbyname(socket.gethostname())
#server = socket.gethostbyname(socket.gethostname) #get the ip address of the curent machine
serverAddr = (serverIP,port) #defining a tuple
format = 'utf-8'
disconnect_message = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(serverAddr)

#----------------------------------------------------------------------------------------------------------------------

class create_new_mail_msg:
  def __init__(self, accountName, password):
    self.type = "create_new_mail"
    self.accountName = accountName
    self.password = password
class sign_in_msg:
  def __init__(self, accountName, password):
    self.type = "sign_in"
    self.accountName = accountName
    self.password = password
class sending_email_msg:
  def __init__(self, accountName, password,toAccounts, ccAccounts, bccAccounts, subject, body, attachedFilesNo):
    self.type = "sending_email"
    self.accountName = accountName
    self.password = password
    self.toAccounts = toAccounts
    self.ccAccounts = ccAccounts
    self.bccAccounts = bccAccounts
    self.subject = subject
    self.body = body
    self.attachedFilesNo = attachedFilesNo
class actions_on_email_msg:
  def __init__(self,accountName, password, emailID,action): 
    # action can be one of three values (normal,archive,delete)
    self.type = "actions_on_email"
    self.accountName = accountName
    self.password = password
    self.emailID = emailID
    self.action = action
class send_email_list_msg:
  def __init__(self,accountName, password,listType):
    #listType can be one of these three values (sent,normal_received,archive_received)
    self.type = "send_email_list"
    self.accountName = accountName
    self.password = password
    self.listType = listType
class email_from_received_list:
  def __init__(
    self,emailID,email_type,
    sent_by,sent_date,
    subject,body,
    to_email_accounts,cc_email_accounts,
    serverFilesLocations):
    self.type = "email_from_received_list"
    self.emailID = emailID
    self.email_type = email_type
    self.sent_by = sent_by
    self.sent_date = sent_date
    self.subject = subject
    self.body = body
    self.to_email_accounts = to_email_accounts
    self.cc_email_accounts = cc_email_accounts
    self.serverFilesLocations = serverFilesLocations
    self.attachedFilesNo = len(str(self.serverFilesLocations).split(",")) 
class email_from_sent_list:
  def __init__(
    self,emailID,sent_by,
    sent_date,subject,body,
    to_email_accounts,cc_email_accounts,bcc_email_accounts,
    serverFilesLocations):
    self.type = "email_from_sent_list"
    self.emailID = emailID
    self.sent_by = sent_by
    self.sent_date = sent_date
    self.subject = subject
    self.body = body
    self.to_email_accounts = to_email_accounts
    self.cc_email_accounts = cc_email_accounts
    self.bcc_email_accounts = bcc_email_accounts
    self.serverFilesLocations = serverFilesLocations
    self.attachedFilesNo = len(str(self.serverFilesLocations).split(","))
class download_attachment_msg:
  def __init__(self,accountName,password,emailID):
    self.type = "download_attachment"
    self.accountName = accountName
    self.password = password
    self.emailID = emailID

#----------------------------------------------------------------------------------------------------------------------

class simpleAcknowledgment: 
  #type can be one of these values
  #client => (ack_email_from_list,ack_attached_file_from_server)
  #server => (ack_create_new_mail,ack_sign_in,ack_sending_email,ack_attached_file_from_client,ack_actions_on_email)
  def __init__(self,ackType,value):
    self.type = ackType
    self.value = value
class send_email_list_ack:
  def __init__(self,value,emailsNum):
    self.type = "send_email_list_ack"
    self.value = value
    self.emailsNum = emailsNum
class download_attachment_ack:
  def __init__(self,value,attachedFilesNo):
    self.type = "download_attachment_ack"
    self.value = value
    self.attachedFilesNo = attachedFilesNo

#----------------------------------------------------------------------------------------------------------------------

def filelocation(accountName,emailId,fileName):
  directoryPath = "/attachments/{}/{}".format(accountName,emailId)
  scriptDirectory = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))).replace("\\", "/")
  directoryPath = scriptDirectory+directoryPath
  Path(directoryPath).mkdir(parents=True, exist_ok=True)
  filePath = directoryPath+"/"+fileName
  return filePath

def send(conn,msg):
  message = pickle.dumps(msg)
  msg_length = len(message) 
  send_length = str(msg_length) 
  send_length = ('{:>'+str(header)+'}').format(send_length) 
  send_length = send_length.encode(format) 
  conn.send(send_length)
  conn.send(message)
def recv(conn):
  msg_length = conn.recv(header).decode(format)
  msg = disconnect_message
  if msg_length:
    msg_length = int(msg_length)
    msg = pickle.loads(conn.recv(msg_length))
  return msg

def sendtext(conn,msg):
  message = msg.encode(format) #encoding the message
  msg_length = len(message) #get the length of the message
  send_length = str(msg_length) #parcing the length from int to string
  send_length = ('{:>'+str(header)+'}').format(send_length) #align right
  send_length = send_length.encode(format) #encoding the length
  conn.send(send_length)
  conn.send(message)
def recvtext(conn):
  msg_length = conn.recv(header).decode(format)
  if msg_length: 
    #the first messsage the clinet send to the server is an empty message which means that
    #we need to ingnore the first message if msg_length: means if the message is not empty string
    msg_length = int(msg_length)
    msg = conn.recv(msg_length).decode(format)
  return msg

def sendFile(conn,accountName,emailID,fileName):
  #fileName: if the file exist in the same directory as the code then just enter the file name => stacker.jpg
  #          else enter the file absoulte path => D:\Term8\Computer Networks\lab\socket programming\sending and receiving files\stacker.jpg
  sendtext(conn,os.path.basename(fileName))
  filepath = filelocation(accountName,emailID,fileName)
  try:
    with open(filepath, "rb") as f:
      while True:
        bytes_read = f.read(BUFFER_SIZE)
        if not bytes_read: 
          conn.sendall(bytes("\0\0",format))
          break
        conn.sendall(bytes_read)
  except Exception as e: 
    conn.sendall(bytes("\0\0",format))
def recvFile(conn,accountName,emailID):
  filename = recvtext(conn)
  filePath = filelocation(accountName,emailID,filename)
  try:
    with open(filePath, "wb") as f:
      while True:
        bytes_read = conn.recv(BUFFER_SIZE)
        if bytes_read[-2:] == bytes("\0\0",format): 
          f.write(bytes_read[:-2])
          break
        f.write(bytes_read)
    storeFileNameInDB(emailID,filename)
  except Exception as e: return simpleAcknowledgment("ack_attached_file_from_client",False)
  return simpleAcknowledgment("ack_attached_file_from_client",True)

def storeFileNameInDB(emailID,fileName):
  dataBase = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="mailserverdb"
  )
  cursor = dataBase.cursor()
  query = "INSERT INTO file (email_id, file_name) VALUES (%s,%s);"
  attributes = (emailID, fileName)
  try:
    cursor.execute(query,attributes)
  except Exception as e: 
    dataBase.close()
    raise Exception("excption in insert file query")
  dataBase.commit()
  dataBase.close()

def authenticate_user(accountName,password):
  dataBase = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="mailserverdb"
  )
  cursor = dataBase.cursor()
  cursor.execute("SELECT CASE WHEN EXISTS (SELECT * FROM account WHERE account_name='{}' && PASSWORD='{}') THEN 'TRUE' ELSE 'FALSE' END as 'account exist';".format(accountName,password))
  result = cursor.fetchall()
  result = result[0][0]
  dataBase.close()
  if result == "TRUE": return True
  else : return False

def create_new_mail(m):
  result = authenticate_user(m.accountName,m.password)
  if result == False: #if this account doesn't exist in the database then create account
    dataBase = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="mailserverdb"
    )
    cursor = dataBase.cursor()
    query = "INSERT INTO account (account_name,PASSWORD) VALUES (%s,%s); "
    attributes = (m.accountName, m.password)
    try:
      cursor.execute(query,attributes)
    except Exception as e: 
      dataBase.close()
      return simpleAcknowledgment("ack_create_new_mail",False)
    dataBase.commit()
    dataBase.close()
    return simpleAcknowledgment("ack_create_new_mail",True)
  else: return simpleAcknowledgment("ack_create_new_mail",False)

def sign_in(m):
  result = authenticate_user(m.accountName,m.password)
  if result == True: return simpleAcknowledgment("ack_sign_in",True)
  else : return simpleAcknowledgment("ack_sign_in", False)

def sending_email(m):
  result = authenticate_user(m.accountName,m.password)
  emailID = -1
  if result == True: 
    dataBase = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="mailserverdb"
    )
    cursor = dataBase.cursor()
    query1 = "START TRANSACTION;"
    query2 = "INSERT INTO email (account_name, subject, body) VALUES (%s,%s,%s);"
    attributes2 = (m.accountName,m.subject,m.body)
    query3 = "INSERT INTO to_cc_bcc (account_name,email_id,type) VALUES   (%s,LAST_INSERT_ID(),%s);"
    attributes3 = []
    for x in m.toAccounts: 
      attributes3.append((x,"to"))
    for x in m.ccAccounts: 
      attributes3.append((x,"cc"))
    for x in m.bccAccounts:
      attributes3.append((x,"bcc"))
    query4 = "SELECT LAST_INSERT_ID() as email_id;"
    query5 = "COMMIT;"
    try:
      cursor.execute(query1)
      cursor.execute(query2,attributes2)
      cursor.executemany(query3,attributes3)
      cursor.execute(query4)
      result = cursor.fetchall()
      emailID = result[0][0]
      cursor.execute(query5)
    except Exception as e: 
      dataBase.close()
      return simpleAcknowledgment("ack_sending_email",False) , emailID
    dataBase.commit()
    dataBase.close()
    return simpleAcknowledgment("ack_sending_email",True) , emailID
  else : return simpleAcknowledgment("ack_sending_email", False) , emailID

def actions_on_email(m):
  result = authenticate_user(m.accountName,m.password)
  if result == True:
    dataBase = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="mailserverdb"
    )
    cursor = dataBase.cursor()
    if m.action == "normal":
      query = "UPDATE to_cc_bcc SET email_type = 'normal'  WHERE  email_id = %s and  account_name = %s;"
    elif m.action == "archive":
      query = "UPDATE to_cc_bcc SET email_type = 'archive'  WHERE  email_id = %s and  account_name = %s;"
    elif m.action == "delete":
      query = "DELETE FROM to_cc_bcc   WHERE  email_id = %s and  account_name = %s;"
    attributes = (m.emailID, m.accountName)
    try:
      cursor.execute(query,attributes)
    except Exception as e: 
      dataBase.close()
      return simpleAcknowledgment("ack_actions_on_email",False)
    dataBase.commit()
    dataBase.close()
    return simpleAcknowledgment("ack_actions_on_email",True)
  else: return simpleAcknowledgment("ack_actions_on_email", False)

def send_email_list(conn,m):
  flag = True
  result = authenticate_user(m.accountName,m.password)
  if result == True:
    dataBase = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="mailserverdb"
    )
    cursor = dataBase.cursor()
    
    if m.listType == "normal_received":
      query = "SELECT  email.email_id,t.email_type, email.account_name as 'sent by' ,DATE_FORMAT(email.sent_date, %s) as sent_date, email.subject,email.body, t.accounts as 'to accounts', cc.accounts AS 'cc accounts',f.files FROM email INNER JOIN (     SELECT      email_id,     email_type,     GROUP_CONCAT(account_name) as 'accounts'     FROM to_cc_bcc     WHERE email_id IN (         SELECT email_id         FROM to_cc_bcc         WHERE account_name = %s 	) AND type = 'to'     GROUP BY email_id ) as t ON t.email_id = email.email_id left JOIN (     SELECT      email_id,     email_type,     GROUP_CONCAT(account_name) as 'accounts'     FROM to_cc_bcc     WHERE email_id IN (         SELECT email_id         FROM to_cc_bcc         WHERE account_name = %s 	) AND type = 'cc'     GROUP BY email_id ) as cc ON cc.email_id = email.email_id LEFT JOIN (     SELECT email.email_id,      GROUP_CONCAT(CONCAT('/',email.account_name,'/',file.email_id, '/', file.file_name)) as files 	FROM file INNER JOIN email ON file.email_id = email.email_id 	GROUP by email_id ) as f ON t.email_id = f.email_id WHERE email.email_id IN (     SELECT to_cc_bcc.email_id     FROM to_cc_bcc     WHERE to_cc_bcc.account_name = %s ) AND t.email_type = 'normal' ORDER BY email.sent_date DESC;"
      attributes = ("%d-%m-%Y",m.accountName, m.accountName, m.accountName)
      cursor.execute(query,attributes)
      result = cursor.fetchall()
      send(conn,send_email_list_ack(True,len(result)))
      for x in result:
        send(conn,email_from_received_list(x[0],x[1],x[2],x[3],x[4],x[5],x[6],x[7],x[8]))
        ack = recv(conn)
        if ack.type == "ack_email_from_list":
          if ack.value == False: flag = False
    elif m.listType == "archive_received":
      query = "SELECT  email.email_id,t.email_type, email.account_name as 'sent by' ,DATE_FORMAT(email.sent_date, %s) as sent_date, email.subject,email.body, t.accounts as 'to accounts', cc.accounts AS 'cc accounts',f.files FROM email INNER JOIN (     SELECT      email_id,     email_type,     GROUP_CONCAT(account_name) as 'accounts'     FROM to_cc_bcc     WHERE email_id IN (         SELECT email_id         FROM to_cc_bcc         WHERE account_name = %s 	) AND type = 'to'     GROUP BY email_id ) as t ON t.email_id = email.email_id left JOIN (     SELECT      email_id,     email_type,     GROUP_CONCAT(account_name) as 'accounts'     FROM to_cc_bcc     WHERE email_id IN (         SELECT email_id         FROM to_cc_bcc         WHERE account_name = %s 	) AND type = 'cc'     GROUP BY email_id ) as cc ON cc.email_id = email.email_id LEFT JOIN (     SELECT email.email_id,      GROUP_CONCAT(CONCAT('/',email.account_name,'/',file.email_id, '/', file.file_name)) as files 	FROM file INNER JOIN email ON file.email_id = email.email_id 	GROUP by email_id ) as f ON t.email_id = f.email_id WHERE email.email_id IN (     SELECT to_cc_bcc.email_id     FROM to_cc_bcc     WHERE to_cc_bcc.account_name = %s ) AND t.email_type = 'archive' ORDER BY email.sent_date DESC;"
      attributes = ("%d-%m-%Y",m.accountName, m.accountName, m.accountName)
      cursor.execute(query,attributes)
      result = cursor.fetchall()
      send(conn,send_email_list_ack(True,len(result)))
      for x in result:
        send(conn,email_from_received_list(x[0],x[1],x[2],x[3],x[4],x[5],x[6],x[7],x[8]))
        ack = recv(conn)
        if ack.type == "ack_email_from_list":
          if ack.value == False: flag = False
    elif m.listType == "sent":
      query = "SELECT  email.email_id, email.account_name as 'sent by' ,DATE_FORMAT(email.sent_date, %s) as sent_date, email.subject,email.body, t.accounts as 'to accounts', cc.accounts as 'cc accounts', bcc.accounts as 'bcc accounts', f.files FROM email INNER JOIN ( 	SELECT email_id,     GROUP_CONCAT(account_name) as 'accounts'     FROM to_cc_bcc WHERE type = 'to' GROUP BY email_id ) as t ON t.email_id = email.email_id LEFT JOIN ( 	SELECT email_id,     GROUP_CONCAT(account_name) as 'accounts'     FROM to_cc_bcc WHERE type = 'cc' GROUP BY email_id ) as cc ON cc.email_id = email.email_id LEFT JOIN ( 	SELECT email_id,     GROUP_CONCAT(account_name) as 'accounts'     FROM to_cc_bcc WHERE type = 'bcc' GROUP BY email_id ) as bcc ON bcc.email_id = email.email_id LEFT JOIN ( 	SELECT email.email_id,     GROUP_CONCAT(CONCAT('/',email.account_name,'/',file.email_id, '/', file.file_name)) as files     FROM file INNER JOIN email ON file.email_id = email.email_id 	GROUP by email_id ) as f ON t.email_id = f.email_id WHERE account_name = %s ORDER BY email.sent_date DESC;"
      attributes = ("%d-%m-%Y",m.accountName)
      cursor.execute(query,attributes)
      result = cursor.fetchall()
      send(conn,send_email_list_ack(True,len(result)))
      for x in result:
        send(conn,email_from_sent_list(x[0],x[1],x[2],x[3],x[4],x[5],x[6],x[7],x[8]))
        ack = recv(conn)
        if ack.type == "ack_email_from_list":
          if ack.value == False: flag = False
    dataBase.close()
    return flag
  else: 
    send(conn,send_email_list_ack(False,0))
    return False

#----------------------------------------------------------------------------------------------------------------------

def download_attachment(conn,m):
  filesAcks = ()
  result = authenticate_user(m.accountName,m.password)
  if result == True:
    dataBase = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="mailserverdb"
    )
    cursor = dataBase.cursor()
    query = "SELECT       CASE WHEN EXISTS        (             SELECT email.email_id, email.account_name FROM email 			WHERE email.email_id = %s AND email.account_name = %s 			UNION ALL 			SELECT to_cc_bcc.email_id, to_cc_bcc.account_name FROM to_cc_bcc 			WHERE to_cc_bcc.email_id = %s AND to_cc_bcc.account_name = %s       )       THEN (SELECT GROUP_CONCAT(file_name) FROM file WHERE email_id = %s GROUP BY email_id)       ELSE 'FALSE' END as 'account exist';"
    attributes = (m.emailID,m.accountName,m.emailID,m.accountName,m.emailID)
    cursor.execute(query,attributes)
    result = cursor.fetchall()
    if result[0][0] != "FALSE":
      result = result[0][0].split(",")
      send(conn,download_attachment_ack(True,len(result)))
      query = "SELECT email.account_name FROM email WHERE email_id = %s;"
      attributes = (m.emailID,)
      cursor.execute(query,attributes)
      sentEmail = cursor.fetchall()
      sentEmail = sentEmail[0][0]
      for x in result:
        sendFile(conn,sentEmail,m.emailID,x)
        ack = recv(conn)
        if ack.type == "ack_attached_file_from_server":
          addedValue = (ack.value,)
          filesAcks = filesAcks + addedValue
      return True,filesAcks
    else:
      send(conn,download_attachment_ack(False,0))
      return False,filesAcks
def handle_client(conn, addr):
  print(f"[NEW CONNECTION] {addr} connected.")
  connected = True
  while connected:
    msg = recv(conn)
    if msg == disconnect_message:
      connected = False
    elif msg.type == "create_new_mail":
      ack = create_new_mail(msg)
      send(conn,ack)
    elif msg.type == "sign_in":
      ack = sign_in(msg)
      send(conn,ack)
    elif msg.type == "sending_email":
      accountName = msg.accountName
      ack, emailID = sending_email(msg)
      send(conn,ack)
      if ack.value == True:
        for i in range(msg.attachedFilesNo):
          ack = recvFile(conn,accountName,emailID)
          send(conn,ack)
    elif msg.type == "actions_on_email":
      ack = actions_on_email(msg)
      send(conn,ack)
    elif msg.type == "send_email_list":
      send_email_list(conn,msg)
    elif msg.type == "download_attachment":
      download_attachment(conn,msg)
    # print(f"[{addr}] {msg}")
  conn.close()


def start():
  server.listen()
  print(f"[LISTENING] Server is listing on {serverIP}")
  while True:
    conn, addr = server.accept()
    thread = threading.Thread(target= handle_client, args=(conn,addr))
    thread.start()
    print(F"[ACTIVE CONNECTIONS] {threading.activeCount() -1}")

print("[STARTING] server is starting...")
start()