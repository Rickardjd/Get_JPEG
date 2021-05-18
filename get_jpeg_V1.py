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
#parser.add_argument("--Period", dest="Period")      #An image every n seconds
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
   #sys.stdout.flush()
    #print("Camera Password:**********")

    
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

LastImageSec = 0
displayFlag = False
while True:

    now = datetime.now()
    CurrentDay = now.strftime("%A")
    CurrentHour = int(now.strftime("%H"))
    CurrentMin = int(now.strftime("%M"))
    CurrentSec  = int(now.strftime("%S"))
    if displayFlag:
        print("\r\nCurrent Time:"+CurrentDay + "/"+str(CurrentHour)+":"+str(CurrentMin))
        print("Start Time:"+config[CurrentDay]['StartHour']+":"+config[CurrentDay]['StartMinute'])
        print("End Time:"+config[CurrentDay]['EndHour']+":"+config[CurrentDay]['EndMinute'])
        print("Period:"+config[CurrentDay]['Period'])
        print("")
        displayFlag = False


    if (config[CurrentDay].getboolean('Recording')):    #Check if day is active for recording.
        if (CurrentHour*60 + CurrentMin) >= (config[CurrentDay].getint('StartHour')*60 + (config[CurrentDay].getint('StartMinute'))):      #Check we are after start time
            if (CurrentHour*60 + CurrentMin) < (config[CurrentDay].getint('EndHour')*60 + (config[CurrentDay].getint('EndMinute'))):       #Check we are before end time
                CurrentTimeSeconds = CurrentHour*3600 + CurrentMin*60 + CurrentSec
                if CurrentTimeSeconds > LastImageSec+config[CurrentDay].getint('Period'):
                    print("\r\n"+str(CurrentTimeSeconds)+"/",end='')
                    print(str(CurrentTimeSeconds+config[CurrentDay].getint('Period')))
                    GetImage()
                    SequNo +=1      #increment Sequence Number 
                    LastImageSec = CurrentTimeSeconds
                    displayFlag = True
                else:       #In recording window but waiting for next image time.
                    print("\rWaiting:"+cursor, end='', flush=True)
                    cursor = cursor[-1] + cursor[:-1]
                    sys.stdout.flush()
                    time.sleep(1)
            else:
                LastImageSec = 0        #Reset Last image as we are beyond end time
                print("\rWaiting for next active period!")
                sys.stdout.flush()
        else:
            print("\rWaiting for next active period!")
            sys.stdout.flush()
    else:
        print("\rDay set to inactive")
        sys.stdout.flush()
    time.sleep(5)

