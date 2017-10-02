import config
import requests
import json


def send_message(response_object):
    params = {"access_token": config.PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = json.dumps(response_object.jsonify())
    print data
    # https://graph.facebook.com/v2.6/me/messages "http://127.0.0.1:5000/print
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
                      params=params,
                      headers=headers,
                      data=data)
    if r.status_code != 200:
        print r.status_code
        print r.text


class ResponseObject(object):

    def __init__(self, sender, content, content_type, quick_reply_id, complement_info):
        self.sender = sender
        self.content = content
        self.content_type = content_type
        self.quick_reply_id = quick_reply_id if quick_reply_id else ""
        self.complement_info = complement_info if complement_info else {}
        self.quick_reply = QuickReplier(quick_reply_id).generate()
        self.json = {}

    def jsonify(self):
        self.text_type()
        self.image_type()
        self.one_trip_type()
        return self.json

    def text_type(self):
        if self.content_type == "text":
            self.json =  {
                "recipient": {
                    "id": self.sender
                },
                "message": {
                    "text": self.content,
                    "quick_replies": self.quick_reply
                }
            }

    def image_type(self):
        if self.content_type == "image":
            self.json = {
                "recipient": {
                    "id": self.sender
                },
                "message": {
                    "attachment": {
                        "type": "image",
                        "payload": {
                            "url": self.content,
                            "is_reusable": False
                        }
                    },
                    "quick_replies": self.quick_reply
                }
            }

    def one_trip_type(self):
        if self.content_type == "one_trip":
            self.json = {
                "recipient": {
                    "id": self.sender
                },
                "message": {
                    "attachment": {
                        "type": "template",
                        "payload": {
                            "template_type": "generic",
                            "elements": [
                                self.one_trip_info(
                                    title="Another trip!",
                                    subtitle="Just arrived at my destiny (rhdzmota).",
                                    image_url=self.complement_info.get("trip_image"),
                                    redirect_url=self.complement_info.get("trip_details")
                                )
                            ]
                        }
                    },
                    "quick_replies": self.quick_reply
                }
            }

    # https://maps.googleapis.com/maps/api/staticmap?size=390x130&path=color:0x004fa0|weight:3|20.6038658,-103.4420784|20.6036837,-103.4415767|20.6036667,-103.4414703|20.6041539,-103.4407715|20.6041539,-103.4407715|20.6029242,-103.4349525|20.6495337,-103.4038708|20.653473522,-103.401138218|20.6838304663,-103.381030805|20.6839465,-103.381239|20.683952985,-103.381650486|20.6839829,-103.3844309|20.6839839,-103.3871013|20.683991,-103.3874586|20.6839651,-103.3887203|20.6838529,-103.3890882|20.6836661,-103.3896925|20.6836661,-103.3896925|20.6825222,-103.3896921|20.682407,-103.3896964|20.6818448,-103.3896959|20.6811365,-103.3897012|20.6805105353,-103.389652791|20.6804741,-103.3896497|20.6804741,-103.3896497&markers=icon:http://pixan.io/dev/crabi-mail-test/public/assets/emails/green-circle.png|20.6038658,-103.4420784&markers=icon:http://pixan.io/dev/crabi-mail-test/public/assets/emails/red-flag.png|20.6804741,-103.3896497&key=AIzaSyDhCWRCvGrLo5YeLrdM-bZAUeETrrLOeZE
    def one_trip_info(self, title, subtitle, image_url, redirect_url):
        return {
            "title": title,
            "subtitle": subtitle,
            "image_url": image_url,
                "default_action": {
                "type": "web_url",
                "url": redirect_url,
                "messenger_extensions": True,
                "webview_height_ratio": "tall",
                "fallback_url": "https://geo-coords-bot.appspot.com/"
            },
            "buttons": [
                self.url_button("CoordBot Home Page", "https://geo-coords-bot.appspot.com/"),
                self.postback_button("Generic", "generic")
            ]
        }

    @staticmethod
    def url_button(title, url):
        return {
            "type": "web_url",
            "url": url,
            "title": title
        }

    @staticmethod
    def postback_button(title, payload):
        return {
            "type": "postback",
            "title": title,
            "payload": payload
        }


class EntryManager(object):

    def __init__(self, entry):
        self.entry = entry
        self.responses = []
        self.message_postback_list = []
        self.delivery_list = []
        self.optin_list = []
        for message_event in entry['messaging']:
            if message_event.get('message') or message_event.get('postback'):
                self.message_postback_list.append(message_event)
            if message_event.get('delivery'):
                self.delivery_list.append(message_event)
            if message_event.get('optin'):
                self.optin_list.append(message_event)

    def send_messages(self):
        self.get_responses()
        messages = []
        for element in self.responses:
            n_responses = len(element["responses"])
            for i in range(n_responses):
                ro = ResponseObject(
                    sender=element["sender"],
                    content=element["responses"][i].get("content"),
                    content_type=element["responses"][i].get("content-type"),
                    quick_reply_id="" if i != (n_responses - 1) else element["quick_reply"],
                    complement_info=element["responses"][i].get("complement-info")
                )
                send_message(ro)
                messages.append(ro.jsonify())
        return messages

    def get_responses(self):
        for message in self.message_postback_list:
            sender, text, payload, attachments = self.extract_elements(message)
            responses, quick_reply = ConversationAgent(text, payload, attachments, sender).speak()
            self.responses.append({
                "sender": sender,
                "original-data": text if text else (payload if payload else (attachments if attachments else "")),
                "responses": responses,
                "quick_reply": quick_reply
            })

    @staticmethod
    def extract_elements(message_element):
        sender = message_element['sender'].get('id')
        text = message_element['message'].get('text')
        payload = None if not message_element['message'].get('quick_reply') else message_element['message']['quick_reply']['payload']
        attachments = message_element['message'].get('attachments')
        return sender, text, payload, attachments


class ConversationAgent(object):

    def __init__(self, text, payload, attachments, sender):
        self.text = text
        self.payload = payload
        self.attachments = attachments
        self.sender = sender
        self.responses = []
        self.quick_reply_id = ""

    def speak(self):
        self.generate_responses()
        return self.responses, self.quick_reply_id

    def generate_responses(self):
        contents, content_types, quick_reply_id, complement_info_list = self.extract_content()
        for content, content_type, complement_info in zip(contents, content_types, complement_info_list):
            self.responses.append(self.single_response(content, content_type, complement_info))
        self.quick_reply_id = quick_reply_id

    def extract_content(self):
        contents, content_types, quick_reply_id, complement_info_list = [""], [""], "", [""]
        if self.payload:
            contents, content_types, quick_reply_id, complement_info_list = PayloadResponses(self.payload).generate()
        elif self.attachments:
            contents, content_types, quick_reply_id, complement_info_list = AttachmentResponses(self.attachments).generate()
        elif self.text:
            contents, content_types, quick_reply_id, complement_info_list = TextResponses(self.text).generate()
        return contents, content_types, quick_reply_id, complement_info_list

    @staticmethod
    def single_response(content, content_type, complement_info):
        return {
            "content": content,
            "content-type": content_type,
            "complement-info": complement_info
        }


class TextResponses(object):

    def __init__(self, text):
        self.text = text
        self.content = None
        self.content_type = None
        self.quick_reply_id = None
        self.complement_info = None

    def generate(self):
        # TODO: check if len of content, content_type and complement_info are the same.
        self.hello_world()
        self.accept()
        self.trip_example()
        self.generic()
        return self.content, self.content_type, self.quick_reply_id, self.complement_info

    def hello_world(self):
        if "hello" in self.text.lower():
            self.content = ["hey :)", "look!"]
            self.content_type = ["text", "text"]
            self.quick_reply_id = "main_menu"
            self.complement_info = [None, None]

    def generic(self):
        if self.content is None:
            self.content = ["Did you said {}?".format(self.text)]
            self.content_type = ["text"]
            self.quick_reply_id = "main_menu"
            self.complement_info = [None]

    def accept(self):
        if ("yes" in self.text.lower()) or ("si" in self.text.lower()):
            self.content = ["Great!"]
            self.content_type = ["text"]
            self.quick_reply_id = "main_menu"
            self.complement_info = [None]

    def trip_example(self):
        if "trip_example" in self.text.lower():
            self.content = ["Great!"]
            self.content_type = ["one_trip"]
            self.quick_reply_id = "main_menu"
            self.complement_info = [
                {
                    "trip_image": "https://maps.googleapis.com/maps/api/staticmap?size=390x130&path=color:0x004fa0|weight:3|20.6038658,-103.4420784|20.6036837,-103.4415767|20.6036667,-103.4414703|20.6041539,-103.4407715|20.6041539,-103.4407715|20.6029242,-103.4349525|20.6495337,-103.4038708|20.653473522,-103.401138218|20.6838304663,-103.381030805|20.6839465,-103.381239|20.683952985,-103.381650486|20.6839829,-103.3844309|20.6839839,-103.3871013|20.683991,-103.3874586|20.6839651,-103.3887203|20.6838529,-103.3890882|20.6836661,-103.3896925|20.6836661,-103.3896925|20.6825222,-103.3896921|20.682407,-103.3896964|20.6818448,-103.3896959|20.6811365,-103.3897012|20.6805105353,-103.389652791|20.6804741,-103.3896497|20.6804741,-103.3896497&markers=icon:http://pixan.io/dev/crabi-mail-test/public/assets/emails/green-circle.png|20.6038658,-103.4420784&markers=icon:http://pixan.io/dev/crabi-mail-test/public/assets/emails/red-flag.png|20.6804741,-103.3896497&key=AIzaSyDhCWRCvGrLo5YeLrdM-bZAUeETrrLOeZE",
                    "trip_details": "https://geo-coords-bot.appspot.com/"
                }
            ]


class PayloadResponses(object):

    def __init__(self, payload):
        self.payload = payload
        self.content = None
        self.content_type = None
        self.quick_reply_id = None
        self.complement_info = None

    def generate(self):
        self.main_menu()
        self.more_options()
        self.op1()
        self.op2()
        self.generic()
        return self.content, self.content_type, self.quick_reply_id, self.complement_info

    def generic(self):
        if self.content is None:
            self.content = ["This is a response for a generic payload"]
            self.content_type = ["text"]
            self.quick_reply_id = "main_menu"
            self.complement_info = [None]

    def main_menu(self):
        if self.payload == "Hello":
            self.content = ["Hello to you.", "punk"]
            self.content_type = ["text", "text"]
            self.quick_reply_id = "main_menu"
            self.complement_info = [None, None]

    def more_options(self):
        if self.payload == "more_options":
            self.content = ["There you go."]
            self.content_type = ["text"]
            self.quick_reply_id = "more_options"
            self.complement_info = [None]

    def op1(self):
        if self.payload == "OP1":
            self.content = ["You selected option 1."]
            self.content_type = ["text"]
            self.quick_reply_id = "main_menu"
            self.complement_info = [None]

    def op2(self):
        if self.payload == "OP2":
            self.content = ["You selected option 2."]
            self.content_type = ["text"]
            self.quick_reply_id = "main_menu"
            self.complement_info = [None]


class AttachmentResponses(object):

    def __init__(self, attachment_dict):
        self.attachment_dict = attachment_dict
        self.content = None
        self.content_type = None
        self.quick_reply_id = None
        self.complement_info = None

    def generate(self):
        self.generic()
        return self.content, self.content_type, self.quick_reply_id, self.complement_info

    def generic(self):
        self.content = ["Nice " + str(self.attachment_dict[0]['type'])]
        self.content_type = ["text"]
        self.quick_reply_id = "main_menu"
        self.complement_info = [None]


class QuickReplier(object):

    def __init__(self, quick_reply):
        self.response = None
        self.reply_type = quick_reply
        self.generate_quick_reply()

    def generate(self):
        return self.response

    def generate_quick_reply(self):
        self.more_options()
        self.main_menu()

    def main_menu(self):
        if (self.reply_type == "main_menu") or (self.response is None):
            self.response = [
                self.quick_text(title="Say Hello", payload="Hello"),
                self.quick_text(title="More opts", payload="more_options")
            ]

    def more_options(self):
        if self.reply_type == "more_options":
            self.response = [
                self.quick_text(title="Option 1", payload="OP1"),
                self.quick_text(title="Option 2", payload="OP2")
            ]

    @staticmethod
    def quick_text(title, payload):
        return {
            "content_type": "text",
            "title": title,
            "payload": payload
        }

