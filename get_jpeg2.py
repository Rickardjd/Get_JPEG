import requests
import time
import sys
from requests.auth import HTTPDigestAuth
from datetime import datetime
import configparser

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--user", dest="user_name")
parser.add_argument("--pass", dest="password")
parser.add_argument("--Filename", dest="Filename")  #Filename to store to excluding extention
parser.add_argument("--Period", dest="Period")      #An image every n seconds
parser.add_argument("--SequNo", dest="SequNo")       #Override sequence number otherwise Sequence number will start at 0


args = parser.parse_args()

Days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Sunday"]     #Hard coded days of the week for simplicity. Move to file or args later


NoImages = 0

    #Setup Sequence Number
if args.SequNo is None:
    SequNo = 0      #Sequence Number for all of the images. Starts at 0
else:
    SequNo = int(args.SequNo)


#---Check if username Set in arguments
if args.user_name is None:
    args.user_name = input("Camera username:")


#---Check if password Set in arguments
if args.password is None:
    args.password = input("Camera Password:")
    print("Camera Password:**********")

    
cursor="oOo...."      #Cursor used for display of waiting

#---------------------Read config file--------------------
config = configparser.ConfigParser()
config.sections()
config.read('get_jpeg.ini')

url = 'http://'+config['DEFAULT']['CameraIP']
print('IPAddress:'+url, end="\r\n")
print('Resolution:'+config['DEFAULT']['Resolution'])
NoImages = 0



#---------------------------------------------------------
#GetImage definition
def GetImage():
    response_data = requests.get(url+'/cgi-bin/camera?resolution='+config['DEFAULT']['resolution'],auth=HTTPDigestAuth(args.user_name, args.password))
    
    #Authentication Success 
    if response_data.status_code == 200:
        now = datetime.now()
        current_time = now.strftime("%j_%Y")
        FileName=str(SequNo)+'_'+current_time+'_'+args.Filename+".jpg"
        f=open(FileName,"wb")
        print('Success! '+FileName)

        f.write(response_data.content)
        f.close()
                
    #Device Not found
    elif response_data.status_code == 404:
        print('Not Found.')
            
    #Authentication failure
    elif response_data.status_code == 401:
        print('Unathorized.')

#--------------------------------------------------------

#Define search function to check days of week
def search(list, value):
    for i in range(len(list)):
        if list[i]==value:
            return True
    return False

#---------------------------------------------------------
while True:
    NoImages +=1
    if NoImages > 1000:
        break
   # Mins = now.strftime("%M")
    print("Waiting:", end='')
    
    now = datetime.now()

    print("")
    print("Recording:"+config[now.strftime("%A")]['Recording'])
    print("Start Hours:"+config[now.strftime("%A")]['StartHour'])
    print("End Hours:"+config[now.strftime("%A")]['EndHour'])
    print("Period:"+config[now.strftime("%A")]['Period'])
    
    NextImageSeconds = (int(now.strftime("%H")*3600)+ (int(now.strftime("%M")) * 60) + (int(now.strftime("%S")))+config[now.strftime("%A")].getint('Period'))
    print("Next Image at "+str(NextImageSeconds))
    while NextImageSeconds > ((int(now.strftime("%H")) * 3600) + (int(now.strftime("%M"))*60) + (int(now.strftime("%S")))):
        print("Current seconds "+str((int(now.strftime("%H")) * 3600) + (int(now.strftime("%M"))*60) + (int(now.strftime("%S")))))
        now = datetime.now()
        print("\rWaiting:"+cursor, end='', flush=True)
        cursor = cursor[-1] + cursor[:-1]
        sys.stdout.flush()
        time.sleep(1)
        
    if config[now.strftime("%A")].getboolean('Recording'):      #Check if Recording is True for this day of the week
        print("\r\nAcive Day")
        StartTime = ((config[now.strftime("%A")].getint('StartHour')) * 60 ) + config[now.strftime("%A")].getint('StartMinute')      #Start time in minutes
        EndTime = ((config[now.strftime("%A")].getint('EndHour')) * 60 ) + config[now.strftime("%A")].getint('EndMinute')            #End time in minutes
        CurrentTime = (int(now.strftime("%H")) * 60) + int(now.strftime("%M"))                                                      #Current time in minutes
        if CurrentTime >= StartTime:
            if CurrentTime < EndTime:
                GetImage()
    else:
        print("\r\nInactive Day")
    SequNo +=1      #increment Sequence Number 

