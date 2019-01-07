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
DAN.profile['df_list']=['tags', 'preferences','allergies','tags_receive','preferences_receive','allergies_receive']
DAN.profile['d_name']=None
DAN.device_registration_with_retry(ServerURL,Reg_addr)
#pasting the new image to pastebin
#making the request and receiving the result
def get_tags(result):
    tags = []
    for each in result['outputs'][0]['data']['concepts']:
        tags.append(each['name'])
    print(tags)
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
    DAN.push('tags',userId,tagsies)
    value = DAN.pull('tags_receive')
    print(value)


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    msg = event.message.text  
    userId = event.source.user_id

    if msg =='allergies':
        line_bot_api.push_message(userId, TextSendMessage(text= 'We want to know about your allergies! Following is a list of them, indicate which ones you have by the index number.'))
        line_bot_api.push_message(userId, TextSendMessage(text='1.Milk\n2.eggs\n3.Fish\n4.Shellfish\n5.Tree nuts\n6.Peanuts\n7.Wheat\n8.Soybeans')) 
        line_bot_api.push_message(userId, TextSendMessage(text='Preface your message by saying \"These are my allergies\".')) 
    if msg[0:22] == 'These are my allergies':
        allergies = ''
        i=4
        msg = msg.split(' ')
        count = 0 
        for i in msg:
            if count>3:
                allergies+=i+','
            count+=1
        DAN.push('allergies',userId,allergies)
        value1 = DAN.pull('allergies_receive')
        print(value1)
    if msg == 'utensils':
        line_bot_api.push_message(userId, TextSendMessage(text='We want to know what utensils you have! Following is a list of them, indicate by the index number of the utensil. '))
        line_bot_api.push_message(userId, TextSendMessage(text='1.oven\n2.mixer\n3.knives\n4.DeepFryer\n5.peeler\n6.blender'))
        line_bot_api.push_message(userId,TextSendMessage(text='Preface your message by saying \'These are my utensils\'.'))
    if msg[0:21] == 'These are my utensils':
        utensils = ''
        msg=msg.split(' ')
        count=0
        for a in msg:
            if count>3:
                utensils+=a+','
            count+=1
        print('these are the utensils i have '+utensils)
        DAN.push('preferences',userId,utensils)
        value2= DAN.pull('preferences_receive')
        print(value2)
    if not userId in user_id_set:
        user_id_set.add(userId)
        saveUserId(userId)

if __name__ == "__main__":

    idList = loadUserId()
    if idList: user_id_set = set(idList)

    try:
        for userId in user_id_set:
            ################################################################################### push welcome text
            try:
                line_bot_api.push_message(userId,TextSendMessage(text='First send an image with the food item you want, then some questions\n follow to make your experience more customized.'))
                line_bot_api.push_message(userId,TextSendMessage(text='After you send the image, please send the word \'allergies\' or \'utensils\''))
            except:
                continue


            ###################################################################################
    except Exception as e:
        print(e)

    app.run('127.0.0.1', port=32768, threaded=True, use_reloader=False)






