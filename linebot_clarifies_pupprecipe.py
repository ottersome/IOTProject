# -*- coding: UTF-8 -*-

# Python module requirement: line-bot-sdk, flask
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage, VideoMessage, \
    AudioMessage, StickerSendMessage
from genderize import Genderize
from clarifai.rest import ClarifaiApp
from clarifai.rest import Image as ClImage
import DAN
from PIL import Image
import urllib.parse,urllib.error,urllib.request,requests,wikipedia,os,json,sys,praw,bs4 as bs,time
#from urllib import parse, request
line_bot_api = LineBotApi(
'2m0NGSS9rxxgiKTKD+yPIRQyr2n7tblyqouzvVe6uG/khmGixOocmMKHe9MsHo3r/45pZXkOO7w+Wh2VfDFr//A/wTrX195HLBKYjyD23J1vcduedkk7vuoGWkvKgLrLfeTLVSmAiBjQ/1XizufZiAdB04t89/1O/w1cDnyilFU=')#Channel Access Token
handler = WebhookHandler('021513e80e6e9b84571f29cc81aedf0a')  # LineBot's Channel secret
user_id_set = set()  # LineBot's Friend's user id
app = Flask(__name__)
###registration to the iottalk server###
###remember to replace with actual idf
ServerURL = 'https://demo.iottalk.tw'
Reg_addr = 'quemeves'
DAN.profile['dm_name']='Recipe_AI'
DAN.profile['df_list']=['tags', 'preferences','allergies','request_in','sendRecipeURL','tags_receive','preferences_receive','allergies_receive', 'URL','request_receive']
DAN.profile['d_name']=None
DAN.device_registration_with_retry(ServerURL,Reg_addr)
#pasting the new image to pastebin
#making the request and receiving the result
def get_tags(result):
    tags = []
    for each in result['outputs'][0]['data']['concepts']:
        tags.append(each['name'])
    #print(tags)
    return tags

def loadUserId():
    try:
        idFile = open('idfile', 'r')
        idList = idFile.readlines()
        print(idList)
        newList=[]
        for item in idList:
            try:
                x=item.split(';')
                newList.append(x[0])
            except:
                continue
        idFile.close()
        #idList = idList[0].split(';')
        print(newList)
        idList.pop()
        return newList
    except Exception as e:
        print(e)
        return None


def saveUserId(userId):
    idFile = open('idfile','a')
    idFile.write(userId+';')
    idFile.close()




@app.route("/", methods=['GET'])
def hello():
    return "HTTPS Test OK."


@app.route("/", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']  # get X-Line-Signature header value
    body = request.get_data(as_text=True)  # get request body as text

    #print("Request body: " + body, "Signature: " + signature)
    try:
        handler.handle(body, signature)  # handle webhook body
    except InvalidSignatureError:
        abort(400)
    return 'OK'

#writes image sent from user to a file called image
@handler.add(MessageEvent, message = ImageMessage)
def handle_message(event):
    userId = event.source.user_id
    message_id = event.message.id
    message_content = line_bot_api.get_message_content(message_id)
    with open('image','wb')as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)
    app = ClarifaiApp(api_key = 'fe71b193ff3f4e95bb996226ed2397a1')
    food='food-items-v1.0'
    model = app.models.get('food-items-v1.0')
    response = model.predict_by_filename('image')
    items = get_tags(response)
    items = items[0:5]
    tagsies= ''
    for things in items:
        tagsies=tagsies+str(things)+','
    tagsies = tagsies[:-1]
    DAN.push('tags',userId,tagsies)
    x= True
    while(x):
        value = DAN.pull('URL')
        if value!=None:
            print('now pulling '+str(value))
            try:  
                address = value[0]
                site = value[1]
                print('sending to '+userId+ " "+str(value[1]))
                line_bot_api.push_message(userId, TextSendMessage(text=site))
                x=False
            except:
                continue      


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    msg = event.message.text  
    userId = event.source.user_id

    if msg =='Allergies':
        line_bot_api.push_message(userId, TextSendMessage(text= 'We want to know about your allergies! Following is a list of them, indicate which ones you have by the index number.'))
        line_bot_api.push_message(userId, TextSendMessage(text='0.Milk\n1.eggs\n2.Fish\n3.Shellfish\n4.Tree nuts\n5.Peanuts\n6.Wheat\n7.Soybeans')) 
        line_bot_api.push_message(userId, TextSendMessage(text='Preface your message by saying \"These are my allergies\".')) 
    if msg[0:22] == 'These are my allergies':
        allergies = ''
        i=4
        msg=msg.strip()
        msg = msg.split(' ')
        count = 0 
        for i in msg:
            if count>3:
                allergies+=i+','
            count+=1
        allergies = allergies[:-1]
        DAN.push('allergies',userId,allergies)
        value1 = DAN.pull('allergies_receive')
        print(value1)
    if msg == 'Utensils':
        line_bot_api.push_message(userId, TextSendMessage(text='We want to know what utensils you have! Following is a list of them, indicate by the index number of the utensil. '))
        line_bot_api.push_message(userId, TextSendMessage(text='0.oven\n1.mixer\n2.knives\n3.DeepFryer\n4.peeler\n5.blender'))
        line_bot_api.push_message(userId,TextSendMessage(text='Preface your message by saying \'These are my utensils\'.'))

    #sending the user's available utensils to iottalk
    if msg[0:21] == 'These are my utensils':
        utensils = ''
        msg=msg.strip()
        msg=msg.split(' ')
        index=0
        for a in msg:
            if index>3:
                utensils+=a+','
            index+=1
        #getting rid of the last comma
        utensils=utensils[:-1]
        print('these are the utensils i have '+utensils)
        DAN.push('preferences',userId,utensils)
        value2= DAN.pull('preferences_receive')
        print(value2)
        
    #getting the user's allergies or utensils
    if msg[0:11] == 'What are my':
        msg=msg.split(' ')
        msg = msg[3]
        DAN.push('request_in',userId,msg)
        y = True
        
        while(y):
            valores = DAN.pull('request_receive')
            print(valores)
            if valores!=None:
                print("receiving "+str(valores))
                
                if valores[2] =='allergies':
                    allergens ={'0':'Milk','1':'eggs','2':'Fish','3':'Shellfish', '4':'Tree Nuts', '5':'Peanuts','6':'Wheat','7':'Soybeans'}
                    valores = valores[1].split(',')
                    stringo='You are allergic to: '
                    for dongxi in valores:
                        stringo+=allergens[dongxi]+','
                    line_bot_api.push_message(userId, TextSendMessage(text=stringo))
                    y=False
                elif valores[2] == 'utensils':
                    utensil_list = {'0':'oven','1':'mixer','2':'knives','3':'DeepFryer','4':'peeler', '5':'blender'} 
                    valores = valores[1].split(',')
                    stringo = 'You currently posses: '
                    for items in valores:
                        stringo+=utensil_list[items]+','
                    print(stringo)
                    line_bot_api.push_message(userId, TextSendMessage(text=stringo)) 
                    y=False
            elif valores ==None:
                print('received a None object for our request')
                y=False
                
    if not userId in user_id_set:
        user_id_set.add(userId)
        saveUserId(userId)

if __name__ == "__main__":

    idList = loadUserId()
    if idList: user_id_set = set(idList)

    try:
        for userId in user_id_set:
            try:
                line_bot_api.push_message(userId,TextSendMessage(text='First send an image with the food item you want, then some questions\n follow to make your experience more customized.'))
                line_bot_api.push_message(userId,TextSendMessage(text='After you send the image, please send the word \'allergies\' or \'utensils\''))
            except:
                continue
    except Exception as e:
        print(e)
    app.run('127.0.0.1', port=32768, threaded=True, use_reloader=False)
    """
    while True:
        pulling = DAN.pull('URL')
        print(' we are pulling in '+str(pulling))
        if pulling!=None:
            try:
                if pulling[1]=='Null'or'null':
                     line_bot_api.pushMessage(pulling[0],TextSendMessage(text='Sorry, could not retrieve a url for your image.'))
                else:   
                    print(str(pulling[0])+" and also getting "+str(pulling[1]))
                    line_bot_api.push_message(pulling[0], TextSendMessage(text=str(pulling[1])))
            except:
                continue  
        pulling2 = DAN.pull('request_in')
    """
