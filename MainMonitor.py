import time
import psutil
import os
import platform
import subprocess
import datetime
import sys
def initfiles():
    if os.path.exists("serviceList.log"):
        os.remove("serviceList.log")
    if os.path.exists("statusLog.log"):
        os.remove("statusLog.log")
    open("serviceList.log","w").close()
    open("statusLog.log","w").close()

def checkingdate(userDate):
    try:
        return datetime.datetime.strptime(userDate,"%Y-%m-%d %H:%M:%S")
    except:
        print("Please enter date by the following format: YYYY-MM-DD HH:MM:SS".format(userDate))
        return False

def pullByDate(date1, date2):
    result=[]
    with open("statusLog.log","r") as log:
        for line in log:
            dateString=line[0:19]
            line_date=checkingdate(dateString)
            if line_date==False:
                print("Please enter date by the following format: YYYY-MM-DD HH:MM:SS, please RERUN")
                exit()
            if date1<=line_date<=date2:
                result.append(line)
    return result

def win_services(log_file):
    dict={}
    date=datetime.datetime.now()
    log_file.write("{}\n".format(date))
    for iter in psutil.win_service_iter():
        service_name=iter.name()
        service_status=iter.status()
        linew="{} {}\n".format(service_name,service_status)
        log_file.write(linew)
        dict[service_name]=service_status
    log_file.write("\n")
    log_file.close()
    return dict

def linux_services(log_file):
    dict={}
    date = datetime.datetime.now()
    output=subprocess.check_output(["service", "--status-all"])
    log_file.write("{}\n".format(date))
    for line in output.split('\n'.encode(encoding='UTF-8')):
        service_name=line[8:]
        service_status=line[3:4]
        linew="{} {}\n".format(service_name,service_status)
        log_file.write(linew)
        dict[service_name]=service_status
    log_file.write("\n")
    log_file.close()
    return dict

def difrence(log_file, s1,s2, platform):
    for key,value in s1.items():
        date=datetime.datetime.now()
        if key not in s2:
            t="Service {} is at sample 1, but not in sample 2.".format(key)
            print(t)
            log_file.write(t+"\n")
            log_file.flush()
        elif value !=s2[key]:
            if platform == "Windows":
                t= "{}: Service '{}' changed status from '{}' to '{}'".format(date, key, value, s2[key])
                log_file.write(t+"\n")
                log_file.flush()
                print(t)
            else:
                status1=value
                status2=s2[key]
                if status1 == b'+':
                    status1="running"
                else:
                    status1="stopped"
                if status2==b'+':
                    status2="running"
                else:
                    status2="stopped"
                t="{}: Service '{}' changed his status from '{}' to '{}'".format(date, key, status1, status2)
                log_file.write(t + "\n")
                log_file.flush
            print(t)
            log_file.write(t+"\n")
            log_file.flush

if(len(sys.argv) <= 1):
    print("Welcome! please use the following format:\n"
          " 'python MainMonitor.py <mode> <seconds> OR <date1> <date2>'\n"
          "Mode can be monitor or manual, if monitor then <seconds>, if manual then <date1> <date>2\n"
          "seconds is the time for the refresh rate\n")
    exit()
if("monitor" == sys.argv[1]):
    if(len(sys.argv) <= 2):
        print("Welcome! please use the following format:\n"
              " 'python MainMonitor.py <mode> <seconds> OR <date1> <date2>'\n"
              "Mode can be monitor or manual, if monitor then <seconds>, if manual then <date1> <date>2\n"
              "seconds is the time for the refresh rate\n")
        exit()
    seconds = sys.argv[2]
    str=">>>> Monitor mode chosen: Refresh rate of {} seconds".format(seconds)
    print(str)

    initfiles()
    platform=platform.system()
    status_log = open("statusLog.log", "a")
    log_file = open("serviceList.log", "a")
    if(platform == "Windows"):
        print(">> windows os")
        dict = win_services(log_file)
        while True:
            my_dict = win_services(open("serviceList.log", "a"))
            time.sleep(float(seconds))
            my_dict2 = win_services(open("serviceList.log", "a"))
            difrence(status_log, my_dict, my_dict2, platform)
    else:
        print(">>>> linux os")
        dict=linux_services(log_file)
        while True:
            my_dict=linux_services(open("serviceList.log","a"))
            time.sleep(float(seconds))
            my_dict2=linux_services(open("serviceList.log","a"))
            difrence(status_log,my_dict,my_dict2,platform)
elif("manual"==sys.argv[1]):
    print(">>>>Manual mode chosen")
    if(len(sys.argv)<=5):
        print("Welcome! please use the following format:\n"
              " 'python MainMonitor.py <mode> <seconds> OR <date1> <date2>'\n"
              "Mode can be monitor or manual, if monitor then <seconds>, if manual then <date1> <date>2\n"
              "seconds is the time for the refresh rate\n")
        exit()
    txt_date1 = sys.argv[2] + " " + sys.argv[3]
    txt_date2 = sys.argv[4] + " " + sys.argv[5]
    date1 = checkingdate(txt_date1)
    date2 = checkingdate(txt_date2)
    if date1 == False or  date2 == False:
        print("Please try again")
        exit()
    lines =pullByDate(date1, date2)
    print(">>> Total events found: " + str(len(lines)))
    for line in lines:
        print(line)
else:
    print("Use 'manual' or 'monitor' mode")
    exit()
