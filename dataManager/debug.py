import time, DAN, requests, random

ServerURL = 'https://demo.iottalk.tw' #with no secure connection
#ServerURL = 'https://DomainName' #with SSL connection
Reg_addr = "Putisooo" #if None, Reg_addr = MAC address

DAN.profile['dm_name']='debugRecipe'
DAN.profile['df_list']=['debugRecipe']
DAN.profile['d_name']= "Putooon" # None for autoNaming
DAN.device_registration_with_retry(ServerURL, Reg_addr)

while True:
#Pull data from a device feature called "Dummy_Control"
    flago = False
    try:
    #Push data to a device feature called "Dummy_Sensor"
        value2="0,1,2"
        DAN.push ('debugRecipe', value2,  value2)


    except Exception as e:
        print(e)
        if str(e).find('mac_addr not found:') != -1:
            print('Reg_addr is not found. Try to re-register...')
            DAN.device_registration_with_retry(ServerURL, Reg_addr)
        else:
            print('Connection failed due to unknow reasons.')
            time.sleep(1)    
        flago = True

    if flago == False :
        break
    time.sleep(0.2)

