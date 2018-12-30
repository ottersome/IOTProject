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
import urllib.parse,urllib.error,urllib.request,requests,wikipedia,os,json,sys,praw,bs4 as bs,time

line_bot_api = LineBotApi(
    'rKM2qY9n+tqDGjPPsvH4u/E16lKk0F9OLKM3LpGsquug2qGGJDkYBKb6H7omveX1tEiLEztK1lk9AS1OVozaA//uXxLmVulJq3Kxis8oV2BtyhWhndyq5haWJkzzawEdvrape4+fWLhjGBcarHD53QdB04t89/1O/w1cDnyilFU=')  # LineBot's Channel access token
handler = WebhookHandler('b46c4a23e6d1e7e24973d20ce9f8f280')  # LineBot's Channel secret
user_id_set = set()  # LineBot's Friend's user id
app = Flask(__name__)


def loadUserId():
    try:
        idFile = open('idfile', 'r')
        idList = idFile.readlines()
        idFile.close()
        idList = idList[0].split(';')
        idList.pop()
        return idList
    except Exception as e:
        print(e)
        return None


def saveUserId(userId):
    idFile = open('idfile', 'a')
    idFile.write(userId + ';')
    idFile.close()


@app.route("/", methods=['GET'])
def hello():
    return "HTTPS Test OK."


@app.route("/", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']  # get X-Line-Signature header value
    body = request.get_data(as_text=True)  # get request body as text
    print("Request body: " + body, "Signature: " + signature)
    try:
        handler.handle(body, signature)  # handle webhook body
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    Msg = event.message.text
    if Msg == 'Hello, world': return
    print('GotMsg:{}'.format(Msg))

    # line_bot_api.reply_message(event.reply_token,TextSendMessage(text="收到訊息!!"))   # Reply API example

    userId = event.source.user_id
    if not userId in user_id_set:
        user_id_set.add(userId)
        saveUserId(userId)

    try:
        line_bot_api.push_message(userId, TextSendMessage(text='Thank you!!, im processing your image'))
        #sticker_message = StickerSendMessage(package_id='106', sticker_id='1')
        line_bot_api.push_message(userId, StickerSendMessage(package_id='1', sticker_id='2'))
        time.sleep(2)
        line_bot_api.push_message(userId, TextSendMessage(text='emmmm...., give me a minute'))
    #######################################################################################  clarifai API
        results = ' '
        app = ClarifaiApp(api_key='fe71b193ff3f4e95bb996226ed2397a1')
        model = app.models.get('food-items-v1.0')
        image = ClImage(
            url= Msg)
        result = model.predict([image])
    #######################################################################################


        for each in result['outputs'][0]['data']['concepts']:
            # print(each['name']+', ',end='')
            # results=results+each['name']+','
            print(each['name'], ' ', each['value'])
            #line_bot_api.push_message(userId, TextSendMessage(text=each['name']))
            # print(results+'\n')

            response = requests.get("http://www.recipepuppy.com/api/?i=" + results + each['name'] + "&q&p=1 ")

            try:
                data = json.loads(response.text)
                results = results + each['name'] + ','
            except:
                pass
        line_bot_api.push_message(userId, TextSendMessage(text='i see '+results))
        print(results)
        time.sleep(3)
        data = json.loads(response.text)
        # for each in data['results']:
        #   print(each['title']+'\n'+'Link\t\t: '+each['href']+'\n'+'Ingredients\t: '+each['ingredients']+'\n'+each['thumbnail']+'\n')
        line_bot_api.push_message(userId, TextSendMessage(text='and here are what you could make'))

        time.sleep(2)
        count=0
        for each in data['results']:
            texts = (each['title'] + '\n' + 'Link\t\t: ' + each['href'] + '\n' + 'Ingredients\t: ' + each['ingredients'])
            print(texts)
            line_bot_api.push_message(userId, TextSendMessage(text= texts))
            count+=1
            if(count==5):
                break
            time.sleep(2)

        line_bot_api.push_message(userId, TextSendMessage(text='hope you enjoy :D'))
        line_bot_api.push_message(userId, StickerSendMessage(package_id='1', sticker_id='132'))

    except:
        print('not an image url!!!!')
        line_bot_api.push_message(userId, TextSendMessage(text='wait...you sent me an invalid url, or did u even send me an image url?!'))
        line_bot_api.push_message(userId, StickerSendMessage(package_id='1', sticker_id='7'))
        pass

if __name__ == "__main__":

    idList = loadUserId()
    if idList: user_id_set = set(idList)

    try:
        for userId in user_id_set:
            ################################################################################### push welcome text


            line_bot_api.push_message(userId, TextSendMessage(text='Hallo there!!!'))
            sticker_message = StickerSendMessage(
                package_id='1', sticker_id='134'
            )
            line_bot_api.push_message(userId, sticker_message)
            line_bot_api.push_message(userId, TextSendMessage(text='I could tell you what dish u can make from the ingredients you have :D'))
            time.sleep(3)
            line_bot_api.push_message(userId, TextSendMessage(text='Please upload your ingredients photo to this link https://postimages.org/ and send me the \'Direct link\' at the bottom of your picture (.png), then i\'ll help you'))
            time.sleep(2)

            line_bot_api.push_message(userId, TextSendMessage(text='i dont expect any photos other than food tho *tehee*'))
            sticker_message = StickerSendMessage(
                package_id='1', sticker_id='10'
            )
            line_bot_api.push_message(userId, sticker_message)



            ###################################################################################
    except Exception as e:
        print(e)

    app.run('127.0.0.1', port=32768, threaded=True, use_reloader=False)

