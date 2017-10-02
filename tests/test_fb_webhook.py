
from app import app
from google.appengine.ext import testbed

import flask
import unittest
import requests
import json
class TestWebhook(unittest.TestCase):
    def set_up(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.app = app


import requests
url = "http://localhost:8080/fb-webhook/geo-coords-bot"
r = requests.get(url)


#from util.uti5l import EntryManager, ResponseObject
from settings import config

# "10155150527234966" "642274965"
# 10156543698309966 20294329
# 5476102035164875110
# 1445499585482198
# 118754562014506
ro = ResponseObject(sender='1445499585482198',
               content="hola",
               content_type="text",
               quick_reply_id="main_menu",
               complement_info=None)

ro.jsonify()

params = {"access_token": config.PAGE_ACCESS_TOKEN}
headers = {"Content-Type": "application/json"}
data = json.dumps(ro.jsonify())
data = json.dumps({'message': {'quick_replies': [{'content_type': 'text',
     'payload': 'Hello',
     'title': 'Say Hello'},
    {'content_type': 'text', 'payload': 'more_options', 'title': 'More opts'}],
   'text': 'Did you said hola?'},
  'recipient': {'id': '1445499585482198'}}
)


r = requests.post("https://graph.facebook.com/v2.6/me/messages",
                      params=params,
                      headers=headers,
                      data=data)

r.text



reply = {'object': 'page', 'entry': [{'id': '118754562014506', 'time': 1506377316941, 'messaging': [{'timestamp': 1506377316689, 'recipient': {'id': '118754562014506'}, 'message': {'seq': 215567, 'mid': 'mid.$cAABsAZUzq79k7FsBUVeuxW5ERwQY', 'text': 'hola'}, 'sender': {'id': '1445499585482198'}}]}]}
reply['entry'][0]


response = {'original-data': 'hola',
  'quick_reply': 'main_menu',
  'responses': [{'complement-info': None,
    'content': 'Did you said hola?',
    'content-type': 'text'}],
  'sender': '1445499585482198'}


em = EntryManager(reply['entry'][0])
em.get_responses()
em.responses
em.send_messages()



import requests
from settings import config
import json

example_data1 = {'object': 'page', 'entry': [{'id': '118754562014506', 'time': 1506377316941, 'messaging': [{'timestamp': 1506377316689, 'recipient': {'id': '118754562014506'}, 'message': {'seq': 215567, 'mid': 'mid.$cAABsAZUzq79k7FsBUVeuxW5ERwQY', 'text': 'hola'}, 'sender': {'id': '1445499585482198'}}]}]}
example_data2 = {'object': 'page', 'entry':
    [{'id': '118754562014506', 'messaging':
        [{'message': {
            'seq': 215641,
            'text': '😂',
            'mid': 'mid.$cAABsAZUzq79k7ceQW1evIJBrvaFT'},
            'recipient': {'id': '118754562014506'},
            'timestamp': 1506401208411,
            'sender': {'id': '1445499585482198'}}],
      'time': 1506401208640}]}

example_data22 = {'object': 'page', 'entry':
    [{'id': '118754562014506', 'messaging':
        [{'message': {
            'seq': 215641,
            'text': 'Hery',
            'mid': 'mid.$cAABsAZUzq79k7ceQW1evIJBrvaFT'},
            'recipient': {'id': '118754562014506'},
            'timestamp': 1506401208411,
            'sender': {'id': '1445499585482198'}}],
      'time': 1506401208640}]}


example_data2 = {'object': 'page', 'entry':
    [{'id': '118754562014506', 'messaging':
        [{'message': {
            'seq': 215641,
            'text': '5',
            'mid': 'mid.$cAABsAZUzq79k7ceQW1evIJBrvaFT'},
            'recipient': {'id': '118754562014506'},
            'timestamp': 1506401208411,
            'sender': {'id': '1445499585482198'}}],
      'time': 1506401208640}]}

fbex = "https://scontent.xx.fbcdn.net/v/t35.0-12/22218165_10156801129279966_787741130_o.png?_nc_ad=z-m&_nc_cid=0&oh=e3755cff6f9840e9423ecd7a8e091133&oe=59D31EF3"

example_data3 = {'object': 'page', 'entry':
    [{'id': '118754562014506', 'messaging':
        [{'message': {
            "mid":"mid.1458696618141:b4ef9d19ec21086067",
            "attachments": [
                {
                    "type": "image",
                    "payload": {
                        "url": fbex
                    }
                }
            ]
        },
            'recipient': {'id': '118754562014506'},
            'timestamp': 1506401208411,
            'sender': {'id': '1445499585482198'}}],
      'time': 1506401208640}]}

params = {"access_token": config.PAGE_ACCESS_TOKEN}
headers = {"Content-Type": "application/json"}

url1 = "https://geo-coords-bot.appspot.com/fb-webhook/geo-coords-bot"
url2 = "http://localhost:8080/fb-webhook/geo-coords-bot"
r = requests.post(url2,
                      params=params,
                      headers=headers,
                      data=json.dumps(example_data3))
r.json()
print(r.text)


attachment_dict = [
                {
                    "type": "image",
                    "payload": {
                        "url": fbex
                    }
                }
            ]
#from util.uti5l import AttachmentResponses
AR = AttachmentResponses(attachment_dict)

AR.generate()


EM = EntryManager(example_data3["entry"][0])
EM.send_messages()


with open('file.html', 'w') as f:
    f.write(r.text)