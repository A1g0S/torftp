#!/usr/bin/env python3

import socket
import argparse
import socks
import sys
import time
from os import system,getcwd
import os

BUFFER = 4094

parser = argparse.ArgumentParser(description='Connect to a ftp server.')

parser.add_argument('--host',
                       metavar='host',
                       type=str,
                       required=True,
                       help='')
parser.add_argument('--port','-p',
                       metavar='port',
                       default=21,
                       type=int,
                       help='servers port'
                       )
parser.add_argument('--tor','-t',
                       required=False,
                       action='store_true',
                       default=False,
                       help='use tor proxy'
                       )
parser.add_argument('--username','-u',
                    metavar='username',
                    default='anonymous',
                    type=str,
                    help='specify username')
parser.add_argument('--password',
                    metavar='password',
                    type=str,
                    default='anonymous',
                    help='specify password')
args = parser.parse_args()

host = args.host
port = args.port
tor = args.tor
username = args.username
password = args.password

def read_from_data_connection(s):
        total_data = ''
        while True:
            data = s.recv(BUFFER)
            total_data = total_data.append(data)
            if not data:
                break
        s.close()
       
        return total_data

def writefile(file,data):
    f=open(file,"wb")
    f.write(data)
    f.close()

def recvall(the_socket,timeout=0.5):
 
    #make socket non blocking
    the_socket.setblocking(0)

    #total data partwise in an array
    total_data=[]
    data=''

    #beginning time
    begin=time.time()
    while 1:
        #if you got some data, then break after timeout
        if total_data and time.time()-begin > timeout:
            break

        #if you got no data at all, wait a little longer, twice the timeout
        elif time.time()-begin > timeout*2:
            break
        
        #recv something
        try:
            data = the_socket.recv(8192).decode("utf-8")
            if data:
                total_data.append(data)
                #change the beginning time for measurement
                begin = time.time()
            else:
                #sleep for sometime to indicate a gap
                time.sleep(0.1)
        except:
            pass
    
    #join all parts to make final string and remove \r\n and b'
    return ''.join(str(x) for x in total_data) 

def recvbytes(s):
        total_data=b""
        while True: 
                data=s.recv(8129)
                if not data:
                        break
                total_data=total_data+data
        return total_data


def sendbytes(s,data):
        data+=b"\n"
        s.sendall(data)


def sendall(s,data):
    data+="\n"
    s.sendall(data.encode("utf-8"))

def data_connection(ip,port):
    data_conn=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    if tor==True:
       data_conn.connect((host,port))
    else:
       data_conn.connect((ip,port))
    return data_conn

def login(s,username,password):
    sendall(s,"USER "+username)
    sendall(s,"PASS "+password)

def pwd(s):
    sendall(s,"PWD")
    data=recvall(s)
    return data

def cd(s,data):
    sendall(s,"CWD "+data)
    data=recvall(s)
    return data

def list(s):
    dcon=passive(s)
    sendall(s,"LIST")
    print(recvall(dcon))
    dcon.close()

def get(s,file):
    dcon=passive(s)
    sendall(s,"RETR "+file)
    writefile(getcwd()+"/"+file,recvbytes(dcon))
    dcon.close()    

def decoder(s,data):
    data=data.split(" ")
    ip_port=data[4]
    ip_port=ip_port.split(",")
    ip=ip_port[0][1:]+"."+ip_port[1]+"."+ip_port[2]+"."+ip_port[3]
    port=(int(ip_port[4])*256)+int(ip_port[5].replace(').',''))
    return ip+":"+str(port)

def passive(s):
    sendall(s,"PASV")
    data=recvall(s)
    ip_port=decoder(s,data)
    ip_port=ip_port.split(":")
    ip=str(ip_port[0])
    port=int(ip_port[1])
    dcon=data_connection(ip,port)
    return dcon

def put(s,file):
    dcon=passive(s)
    sendall(s,"STOR "+os.path.basename(file))
    f=open(file,"rb")
    sendbytes(dcon,f.read())
    f.close()

if __name__ == "__main__":
    if tor==True:
       socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
       socket.socket = socks.socksocket
   
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((host,port))
    banner = recvall(s)
    print(banner)
    login(s,username,password)
    recvall(s)
    logged = recvall(s)
    if "530" in logged:
       print(logged)
       sys.exit()
    
    print(logged)
    try:
    while True:
      print(recvall(s))
      cwd=pwd(s)
      cwd=cwd.split(" ")
      cwd=cwd[1]
      cwd=cwd.replace("'",'')
      cmd=str(input("("+username+")-["+cwd+"]"+"\n$"))
      if(cmd=="CWD" or cmd =="cwd"):
        print(pwd(s))
      elif(cmd[:2]=="cd" or cmd[:2]=="CD"):
        print(cd(s,cmd[3:]))
      elif(cmd=="exit" or cmd=="EXIT" or cmd=="quit" or cmd=="QUIT"):
        s.close()
        sys.exit()
      elif(cmd=="ls" or cmd=="LS"):
        list(s)
      elif(cmd==""):
         continue
      elif(cmd=="clear" or cmd=="CLEAR"):
          system("clear")
      elif(cmd[:2]=="rm" or cmd[:2]=="RM"):
          sendall(s,"DELE "+cmd[3:])
          print(recvall(s))
      elif(cmd[:5]=="mkdir" or cmd[:5]=="MKDIR"):
          sendall(s,"MKD "+cmd[6:])
          print(recvall(s))
      elif(cmd[:5]=="rmdir" or cmd[:5]=="RMDIR"):
          sendall(s,"RMD "+cmd[6:])
          print(recvall(s))
      elif(cmd[:3]=="get" or cmd[3:]=="GET"):
          get(s,cmd[4:])
      elif(cmd[:3]=="put" or cmd[3:]=="PUT"):
          put(s,cmd[4:])
      elif(cmd=="help" or cmd =="HELP"):
          print("\n\t\t  CWD :return the current working directory\n \
                 ls :return the content of a directory\n \
                 exit :drop the connection and exit\n \
                 clear :clear the screen\n \
                 rm :remove a file\n \
                 rmdir :remove a directory\n \
                 mkdir :make a directory\n \
                 get :download a file\n \
                 ")
      else:
        sendall(s,cmd)
        print(recvall(s))
    except:
      s.close()
      sys.exit()
