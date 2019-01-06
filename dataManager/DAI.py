import time, DAN, requests, random
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode 

ServerURL = 'https://demo.iottalk.tw' #with no secure connection
#ServerURL = 'https://DomainName' #with SSL connection
Reg_addr = "Puto el que lo lea" #if None, Reg_addr = MAC address

DAN.profile['dm_name']='recipeFinder'
DAN.profile['df_list']=['saveAllergens', 'saveUtensils']
DAN.profile['d_name']= "Puto el que lo lea" # None for autoNaming
DAN.device_registration_with_retry(ServerURL, Reg_addr)
connection = None
#let us create our boolean arrays 
allergies = [None] * 8

try:
    connection = mysql.connector.connect(host='localhost',database='USERS',user="iot",password="tumadre")
except mysql.connector.Error as error :
    connection.rollback() #rollback if any exception occured
    print("Failed inserting record into python_users table {}".format(error))

while True:
    #Pull data from a device feature called "Dummy_Control"
    try:
        value1=DAN.pull('saveAllergens')
        if value1 != None:
            #We receive the input now we parse it into the database
            # they will be devided by 
            tempList = value1.split(",")
            i = 0
            while i < len(tempList):
                print("Esta : "+tempList[i])
                i += 1
            print (value1[0])

    #Push data to a device feature called "Dummy_Sensor"
        #value2=random.uniform(1, 10)
        #DAN.push ('Dummy_Sensor', value2,  value2)

    except Exception as e:
        print(e)
        if str(e).find('mac_addr not found:') != -1:
            print('Reg_addr is not found. Try to re-register...')
            DAN.device_registration_with_retry(ServerURL, Reg_addr)
        else:
            print('Connection failed due to unknow reasons.')
            time.sleep(1)    

    time.sleep(0.2)

