# -*- coding:utf-8 -*-
from __future__ import print_function
import schedule,os,time,ctypes,sys,winreg,win32con
from datetime import datetime
import logging as l

settings = {}
l.getLogger().setLevel(l.DEBUG)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def runTasks():
    l.info("Will clean the temp folder every " + settings["CleanHours"] + " hours.")
    os.system("mkdir " + settings["TempFilePath"])
    while True: 
        schedule.run_pending()
        time.sleep(10)

def cleanFolder():
    tfp = settings["TempFilePath"]
    l.info("Folder cleaned at " + datetime.now().isoformat() + ".")
    os.system("rmdir /s /q " + tfp)
    os.system("mkdir " + tfp)

def Judge_Key(key_name,
    reg_root=win32con.HKEY_CURRENT_USER,
    reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",):
    reg_flags = win32con.WRITE_OWNER | win32con.KEY_WOW64_64KEY | win32con.KEY_ALL_ACCESS
    try:
        key = winreg.OpenKey(reg_root, reg_path, 0, reg_flags)
        location, type = winreg.QueryValueEx(key, key_name)
        print("Key exists.")
        feedback=0
    except FileNotFoundError as e:
        print("Key doesn't exist.",e)
        feedback =1
    except PermissionError as e:
        print("Permission denied.",e)
        feedback = 2
    except:
        print("Error.")
        feedback = 3
    return  feedback

def checkStartup():
    l.info("Checking self-startup file...")
    auto_startup_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
    if Judge_Key("tfManager",win32con.HKEY_CURRENT_USER,auto_startup_path)!=0:
        l.warning("Missing self-startup register. Try to create...")
        r = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER,auto_startup_path,0,winreg.KEY_SET_VALUE)
        winreg.SetValueEx(r,"tfManager",0,winreg.REG_SZ,'"pythonw ' + __file__ + '"')
        l.info("Create files finished.")
    return 0

def readSettings():
    l.info("Reading Settings.conf...")
    f = open("Settings.conf","r")
    for line in f:
        if line[0]!="#" and line[0]!="\n":
            k = line.split('=')[1]
            if k[-1]=="\n":
                k = k[0:-1]
            if k[0]=='"':
                k = k[1:-1]
            settings[line.split('=')[0]] = k
    l.info("Read finished.")
    print(settings)
    return 0

if is_admin():
    readSettings()
    checkStartup()
    schedule.every(int(settings["CleanHours"])).hours.do(cleanFolder)
    runTasks()
else:
    l.critical("No administrator privileges.The program will end NOW.")
    sys.exit()