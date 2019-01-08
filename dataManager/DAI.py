import urllib.parse,urllib.error,urllib.request,requests,os,json,sys,bs4 as bs,time
import time, DAN, requests, random
import pprint
import mysql.connector

ServerURL = 'https://demo.iottalk.tw' #with no secure connection
#ServerURL = 'https://DomainName' #with SSL connection
Reg_addr = "putizo" #if None, Reg_addr = MAC address

DAN.profile['dm_name']='recipioData'
DAN.profile['df_list']=['sendReply','sendRecipeUrl','saveAllergens', 'saveUtensils','request','receiveTags']
DAN.profile['d_name']= "recipio" # None for autoNaming
allergiesArr =['Milk','Egg','Fish','Shellfish','TreeNuts','Peanuts','Wheat','Soybean']
DAN.device_registration_with_retry(ServerURL, Reg_addr)
connection = None
#let us create our boolean arrays 
allergies = [0] * 8
utensils = [0] * 6
def storeUtensils(value1):
    #We receive the input now we parse it into the database
    # they will be devided by 
    print("The id is : "+value1[0])
    print("Temp list is : "+value1[1])
    tempList = value1[1].split(",")
    i = 0
    while i < len(utensils):
        utensils[i] = 0
        i += 1
    i =0
    while i < len(tempList):
        print("Esta : "+tempList[i])
        utensils[int(tempList[i])] = 1;
        i+=1

    i=0
    print("Your utensils are :")
    while i< len(utensils):
        if(utensils[i] == 1):
            print(i)
        i+=1
    #Getting them inside the database:
    cursor = connection.cursor()
    values = [value1[0]]
    values.extend(utensils)
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(values);
    sql = "INSERT INTO equipment VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(sql,values)
    connection.commit()

def storeAllergens(value1):
    #We receive the input now we parse it into the database
    # they will be devided bystore 
    print("The id is : "+value1[0])
    print("Temp list is : "+value1[1])
    tempList = value1[1].split(",")
    i = 0
    while i < len(allergies):
        allergies[i] = 0
        i += 1
    i =0
    while i < len(tempList):
        print("Esta : "+tempList[i])
        allergies[int(tempList[i])] = 1;
        i+=1

    i=0
    print("Your allergies are :")
    while i< len(allergies):
        if(allergies[i] == 1):
            print(i)
        i+=1
    #Getting them inside the database:
    cursor = connection.cursor()
    values = [value1[0]]
    values.extend(allergies)
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(values);
    sql = "INSERT INTO allergens VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(sql,values)
    connection.commit()


def receiveTags(value1):
    print("This is what i get : "+value1[1])
    tempList = value1[1].split(",")
    finalUrl =""
    try:
        cursor = connection.cursor(buffered=True)
        #Get alerlgies
        sql = "SELECT * FROM allergens WHERE user = %s"
        print("This is the user id: "+value1[0])
        valuesto = [value1[0]]
        cursor.execute(sql,valuesto)

        resulto= cursor.fetchall()
        print(resulto)
        i =1
        finalResult =""
        isFirst = True
        while i < len(resulto[0]):
            if(resulto[0][i] == 1):
                print("This is the first allergies: "+allergiesArr[int(i-1)])
                print("Allergic to: "+str(i-1))
                if isFirst == False:
                    finalResult = finalResult+","
                tempList.append("-"+allergiesArr[int(i-1)])
                finalResult = finalResult+str(i-1)
                isFirst = False
            i+=1
        print("Final result is : "+finalResult)

        results =""
        stringo =""
        isFirst = True
        for each in tempList:
            print("Using this tag now: "+each)
            if(isFirst != True):
                stringo +="%2C"
            stringo += each
            isFirst = False
        #http://www.recipepuppy.com/?i=-peanuts%2C+tomato&q=tomato+peanuts
        print("This is the final stringo baby : "+stringo)  
        response = requests.get("http://www.recipepuppy.com/api/?i="+ stringo + "&q&p=1 ")
        try:
            data = json.loads(response.text)
            results = results + each + ','
        except:
            pass
        print(results)
        data = json.loads(response.text)
        # for each in data['results']:
        #   print(each['title']+'\n'+'Link\t\t: '+each['href']+'\n'+'Ingredients\t: '+each['ingredients']+'\n'+each['thumbnail']+'\n')
        count=0
        for each in data['results']:
            texts = (each['title'] + '\n' + 'Link\t\t: ' + each['href'] + '\n' + 'Ingredients\t: ' + each['ingredients'])
            finalUrl = each['href']
            print(texts)
            count+=1
            if(count==1):
                break
        cursor.close()
    except:
        print('Something happened when getting the urls')
        pass

    #now try to return the url
    DAN.push ('sendRecipeUrl', value1[0],  finalUrl)

def requesto(value1):
    cursor = connection.cursor(buffered=True)
    sql =""
    values = None
    if(value1[1] == "utensils"):
        sql = "SELECT * FROM equipment WHERE id = %s"
        print("Nos meditmos autensils")
    elif(value1[1] == "allergies"):
        sql = "SELECT * FROM allergens WHERE user = %s"
        print("Nos meditmos allergies")

    values=[value1[0]]
    print("This is your id : "+str(value1[0]))
    cursor.execute(sql,values)
    connection.commit()
    result = cursor.fetchall()
    print("Ya te muestro el result papi")
    print(result)
    i =1
    finalResult =""
    isFirst = True
    while i < len(result[0]):
        if(result[0][i] == 1):
            print("Allergic to: "+str(i-1))
            if isFirst == False:
                finalResult = finalResult+","
            finalResult = finalResult+str(i-1)
            isFirst = False
        i+=1
    print("Final result is : "+finalResult)
    cursor.close()
    DAN.push ('sendReply', value1[0], finalResult,value1[1])
try:
    connection = mysql.connector.connect(host='localhost',database='USERS',user="iot",password="tumadre")
except mysql.connector.Error as error :
    print("Failed inserting record into python_users table {}".format(error))

while True:
    #Pull data from a device feature called "Dummy_Control"
    try:
        value1=DAN.pull('saveAllergens')
        if value1 != None:
            storeAllergens(value1)
        value1=DAN.pull('saveUtensils')
        if value1 != None:
            storeUtensils(value1)
        value1=DAN.pull('request')
        if value1 != None:
            requesto(value1)
        value1=DAN.pull('receiveTags')
        if value1 != None:
            receiveTags(value1)
            
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

