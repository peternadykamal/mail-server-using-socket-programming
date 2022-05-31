from cgi import print_arguments
from email import message
import email
from http import client
from secrets import choice
from socket import socket
import socket
import pickle
import os
from pathlib import Path
from urllib import response

BUFFER_SIZE = 4096
header = 64
port = 5050
serverIP = socket.gethostbyname(socket.gethostname())
serverAddr = (serverIP,port)
format = 'utf-8'
disconnect_message = "!DISCONNECT"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(serverAddr)

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
    self.attachedFilesNo = len(self.serverFilesLocations.split(",")) 
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
    self.attachedFilesNo = len(self.serverFilesLocations.split(","))
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

def filelocation(fileName):
  directoryPath = "/temp"
  scriptDirectory = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))).replace("\\", "/")
  directoryPath = scriptDirectory+directoryPath
  Path(directoryPath).mkdir(parents=True, exist_ok=True)
  filePath = directoryPath+"/"+fileName
  return filePath

def send(msg):
  message = pickle.dumps(msg)
  msg_length = len(message)
  send_length = str(msg_length)
  send_length = ('{:>'+str(header)+'}').format(send_length)
  send_length = send_length.encode(format)
  client.send(send_length)
  client.send(message)
def recv() :
  msg_length = client.recv(header).decode(format) 
  if msg_length:
    msg_length = int(msg_length)
    msg = pickle.loads(client.recv(msg_length))
  return msg

def sendtext(msg):
  message = msg.encode(format) #encoding the message
  msg_length = len(message) #get the length of the message
  send_length = str(msg_length) #parcing the length from int to string
  send_length = ('{:>'+str(header)+'}').format(send_length) #align right
  send_length = send_length.encode(format) #encoding the length
  client.send(send_length)
  client.send(message)
def recvtext() :
  msg_length = client.recv(header).decode(format)
  if msg_length:
    msg_length = int(msg_length)
    msg = client.recv(msg_length).decode(format)
  return msg

def sendFile(fileName):
  #fileName: if the file exist in the same directory as the code then just enter the file name => stacker.jpg
  #          else enter the file absoulte path => D:\Term8\Computer Networks\lab\socket programming\sending and receiving files\stacker.jpg
  sendtext(os.path.basename(fileName))
  fileName = fileName.replace("\\", "/")
  try:
    with open(fileName, "rb") as f:
      while True:
        bytes_read = f.read(BUFFER_SIZE)
        if not bytes_read: 
          client.sendall(bytes("\0\0",format))
          break
        client.sendall(bytes_read)
  except Exception as e:
    client.sendall(bytes("\0\0",format))
def recvFile():
  filename = recvtext()
  filePath = filelocation(filename)
  with open(filePath, "wb") as f:
    while True:
      bytes_read = client.recv(BUFFER_SIZE)
      if bytes_read[-2:] == bytes("\0\0",format): 
        f.write(bytes_read[:-2])
        break
      f.write(bytes_read)

def create_new_mail(email,password):
  msg = create_new_mail_msg(email,password)
  send(msg)
  respond = recv()
  if respond.type == "ack_create_new_mail":
    if respond.value == True : return True
    else : return False
  else : return False

def sign_in(email,password):
  msg = sign_in_msg(email,password)
  send(msg)
  respond = recv()
  if respond.type == "ack_sign_in":
    if respond.value == True : return True
    else : return False
  else : return False

def sending_email(accountName, password,toAccounts, ccAccounts, bccAccounts, subject, body, attachedFilesNo,fileLocations):
  filesAcks = ()
  msg = sending_email_msg(accountName, password,toAccounts, ccAccounts, bccAccounts, subject, body, attachedFilesNo)
  send(msg)
  respond = recv()
  if respond.type == "ack_sending_email":
    if respond.value == True :
      for filepath in fileLocations:
        sendFile(filepath)
        ack = recv()
        if ack.type == "ack_attached_file_from_client":
          addedValue = (ack.value,)
          filesAcks = filesAcks + addedValue
      return True , filesAcks
    else : return False , filesAcks
  else : return False ,filesAcks

def actions_on_email(accountName, password, emailID,action):
  msg = actions_on_email_msg(accountName, password, emailID,action)
  send(msg)
  respond = recv()
  if respond.type == "ack_actions_on_email":
    if respond.value == True : return True
    else : return False
  else : return False

def send_email_list(accountName, password,listType):
  emailsList = []  
  msg = send_email_list_msg(accountName, password,listType)
  send(msg)
  respond = recv()
  if respond.type == "send_email_list_ack":
    if respond.value == True : 
      for i in range(respond.emailsNum):
        m = recv() #client will recieve email object 
        emailsList.append(m) #put this email object in a list
        send(simpleAcknowledgment("ack_email_from_list",True)) #send an ack
      return True , emailsList
    else : return False , emailsList
  else : return False , emailsList

def download_attachment(accountName,password,emailID):
  msg = download_attachment_msg(accountName,password,emailID)
  send(msg)
  respond = recv()
  if respond.type == "download_attachment_ack":
    if respond.value == True :
      for i in range(respond.attachedFilesNo):
        recvFile()
        send(simpleAcknowledgment("ack_attached_file_from_server",True))
      return True
    else : return False
  else : return False

def flushTempFolder():
  directoryPath = "/temp"
  scriptDirectory = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))).replace("\\", "/")
  directoryPath = scriptDirectory+directoryPath
  print(directoryPath)
  answer = input("are you sure you want to delete(y/n)")
  if answer == 'y':
    for f in os.listdir(directoryPath):
      os.remove(os.path.join(directoryPath, f))


# function gui can call and use,
#--------------------------------------
# create_new_mail(email,password)
# return True if success, False if not

# sign_in(email,password)
# returns True if success, False if not

# sending_email(accountName, password,toAccounts, ccAccounts, bccAccounts, subject, body, attachedFilesNo,fileLocations)
# returns (ack,filesAcks) where ack : is the ack that email is recieved by server and filesAcks : is the ack that files are recieved by server

# actions_on_email(accountName, password, emailID,action) action = "normal" OR "archive" OR "delete"
# return True if success, False if not

# send_email_list(accountName, password,listType) listType = "sent" OR "normal_received" OR "archive_received"
# returns (ack, send_email_list_msg object) OR (ack, email_from_received_list object)

# download_attachment(accountName,password,emailID)
# returns True if success, False if not

# flushTempFolder()
# just remove every file inside the temp folder

while True:
  print("Input 0 To Close The Connection")
  print("1. create_new_mail \n2. sign in\n3.sending email\n4.certain received email option\n5. return email list\n6.download attachment of specific email\n7.flush temp folder")
  m = input("enter your choise>> ")
  if m == "0":
    send(disconnect_message)
    break
  elif m == "1": 
    email = input("enter new email: ")
    password = input("enter new password more than or equal 10 characters: ")
    print(create_new_mail(email,password))
  elif m == "2":
    email = input("enter your email: ")
    password = input("enter your password: ")
    print(sign_in(email,password))
  elif m == "3":
    # email = input("enter your email: ")
    # password = input("enter your password: ")
    
    # toAccounts = ()
    # x = input("enter number of to accounts: ")
    # for i in range(int(x)):
    #   addedValue = (input("enter to account: "),)
    #   toAccounts = toAccounts + addedValue
    
    # ccAccounts = ()
    # x = input("enter number of cc accounts: ")
    # for i in range(int(x)):
    #   addedValue = (input("enter cc account: "),)
    #   ccAccounts = ccAccounts + addedValue
    
    # bccAccounts = ()
    # x = input("enter number of bcc accounts: ")
    # for i in range(int(x)):
    #   addedValue = (input("enter bcc account: "),)
    #   bccAccounts = bccAccounts + addedValue
    
    # subject = input("enter email subject: ")
    # body = input("enter email body: ")
    
    # fileLocations = ()
    # attachedFilesNo = input("enter number of attached files: ")
    # for i in range(int(attachedFilesNo)):
    #   addedValue = (input("enter file path: "),)
    #   fileLocations = fileLocations + addedValue
    
    # print(sending_email(email,password,toAccounts,ccAccounts,bccAccounts,subject,body,attachedFilesNo,fileLocations))
        print(sending_email(
      "mahmoud3erfan@computerdep.eg","0123456789",
      ("seifossama@computerdep.eg",),("moroelmasery@computerdep.eg",),
      ("peternady@computerdep.eg",),"new email with new files","hellooooo team",
      2,("D:\wallpapers\gKov2He.png","D:\Term8\Computer Networks\sheets\CC431 - Sheet 1.pdf")
    ))
  elif m == "4":
    email = input("enter your email: ")
    password = input("enter your password: ")
    emailID = input("enter emailID: ")
    print("1.change to normal\n2.change to archive\n3.delete this emai")
    n = input("enter your choise>> ")
    if n=="1" : answer = "normal"
    elif n=="2" : answer = "archive"
    elif n=="3" : answer = "delete"
    print(actions_on_email(email,password,emailID,answer))
  elif m == "5":
    email = input("enter your email: ")
    password = input("enter your password: ")
    print("1.sent emails list\n2.normal received emails list\n3.archive received emails list")
    n = input("enter your choise>> ")
    if n=="1" : answer = "sent"
    elif n=="2" : answer = "normal_received"
    elif n=="3" : answer = "archive_received"
    ack,elist = send_email_list(email,password,answer)
    # ack,elist = send_email_list("peternady@computerdep.eg","0123456789","sent")
    print(ack)
    if(len(elist)>0 and elist[0].type == "email_from_received_list"):
      for x in elist:
        print(x.emailID)
        print(x.email_type)
        print(x.sent_by)
        print(x.sent_date)
        print(x.subject)
        print(x.body)
        print(x.to_email_accounts)
        print(x.cc_email_accounts)
        print(x.serverFilesLocations)
        print(x.attachedFilesNo)
    elif(len(elist)>0 and elist[0].type == "email_from_sent_list"):
      for x in elist:
        print(x.emailID)
        print(x.sent_by)
        print(x.sent_date)
        print(x.subject)
        print(x.body)
        print(x.to_email_accounts)
        print(x.cc_email_accounts)
        print(x.bcc_email_accounts)
        print(x.serverFilesLocations)
        print(x.attachedFilesNo)
  elif m == "6":
    email = input("enter your email: ")
    password = input("enter your password: ")
    emailID = input("enter emailID: ")
    print(download_attachment(email,password,emailID))
  elif m == "7":
    flushTempFolder()