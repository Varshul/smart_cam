from flask import Flask, request
import requests
import re
import cognitive_face as CF
import dropbox
from picamera import PiCamera 
from time import sleep 
import time 
app = Flask(__name__)

ACCESS_TOKEN = ""
VERIFY_TOKEN = ""

def reply(user_id, msg):
    data = {
        "recipient": {"id": user_id},
        "message": {"text": msg}
    }
    resp = requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + ACCESS_TOKEN, json=data)
    print(resp.content)

def reply_image(user_id, image_url):
    data = {
        "recipient": {"id": user_id},
        "message": {"attachment":{
                    "type":"image",
                    "payload":{
                    "url":image_url
                }
            }
        }
    }
    resp = requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + ACCESS_TOKEN, json=data)
    print(resp.content)

def reply_with_image(user_id):
    camera = PiCamera()
    img_name = str(time.time())
    image_name = '/home/pi/Desktop/detect_face/'+ img_name +'-image.jpg'

    camera.capture(image_name)
    camera.stop_preview()
    camera.close()
    dbx = dropbox.client.DropboxClient("0XawiRJcRPAAAAAAAAAACjsBHNbsJZOJ27uyxHQAvwTXp2c2SKYs2gIYBH2lQqYN")
    target_file = '/Images/' + img_name + '-image.png'

    f = open('/home/pi/Desktop/detect_face/' + img_name + '-image.jpg','rb')
    resp = dbx.put_file(target_file,f)

    dbx = dropbox.Dropbox("0XawiRJcRPAAAAAAAAAACjsBHNbsJZOJ27uyxHQAvwTXp2c2SKYs2gIYBH2lQqYN")
    link = dbx.sharing_create_shared_link(target_file)

    dl_url= re.sub(r"\?dl\=0","?dl=1",link.url)
    KEY =  'bb8ebf32219a415fa5ae838cb046c3be'
    CF.Key.set(KEY)

    img_url = dl_url
    result = CF.face.detect(img_url,landmarks=True,attributes='age,gender,smile,facialHair,glasses')
    
    if len(result) != 0:
        reply(user_id,"coming from pi : gender - " + result[0]['faceAttributes']['gender'] + '\n age - ' + str(result[0]['faceAttributes']['age']))
        reply_image(user_id,dl_url)
    else :
        reply(user_id,"coming from pi : no person found")
        reply_image(user_id,dl_url)

@app.route('/', methods=['GET'])
def handle_verification():
    if request.args['hub.verify_token'] == VERIFY_TOKEN:
        return request.args['hub.challenge']
    else:
        return "Invalid verification token"


@app.route('/', methods=['POST'])
def handle_incoming_messages():
    data = request.json
    sender = data['entry'][0]['messaging'][0]['sender']['id']
    message1 = data['entry'][0]['messaging'][0].get('message',None)
    if message1 == None:
        return 'OK'
    message = data['entry'][0]['messaging'][0]['message'].get('text',None)
    print message
    if message != None :
	if re.search('capture', message) :
    	    reply_with_image(sender)
    	    return 'OK'
	if re.search('echo', message) :
    	    reply(sender, message)
	elif re.search('image', message) :
            reply_image(sender, 'https://yt3.ggpht.com/-v0soe-ievYE/AAAAAAAAAAI/AAAAAAAAAAA/OixOH_h84Po/s900-c-k-no-mo-rj-c0xffffff/photo.jpg')
        else :
            reply(sender,'recvd')
    else :
        return 'OK'
    '''
    print(data['entry'][0]['messaging'][0])
    if data['entry'][0]['messaging'][0]['message']['text'] != None :
	reply(sender,data['entry'][0]['messaging'][0]['message']['text'] )
    if data['entry'][0]['messaging'][0]['read']['watermark'] != None :
        reply(sender,'You Read The Message ' + data['entry'][0]['messaging'][0]['read']['watermark'] )
    '''

    return "ok"


if __name__ == '__main__':
    app.run(debug=True)

