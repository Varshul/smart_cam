from flask import Flask, request
import requests
import re
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
    message = data['entry'][0]['messaging'][0]['message'].get('text',None)
    if message != None :
	    if re.search('echo', message) :
    		reply(sender, message)
	    elif re.search('image', message) :
                reply_image(sender, 'https://yt3.ggpht.com/-v0soe-ievYE/AAAAAAAAAAI/AAAAAAAAAAA/OixOH_h84Po/s900-c-k-no-mo-rj-c0xffffff/photo.jpg')
    else :
        reply(sender, 'recvd')
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

