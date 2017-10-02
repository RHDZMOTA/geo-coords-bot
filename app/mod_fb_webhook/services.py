from settings import config
from app.mod_fb_webhook.models import QuickText, QuickReply, ResponsePacket, SingleResponse, \
    TextMessage, ImageMessage, MessageInfo
from google.appengine.api import urlfetch
from flask import jsonify
from util.cloud_vision import OCR
import requests
import json

urlfetch.set_default_fetch_deadline(60)


class FacebookWebHook(object):
    HUB_MODE = config.HUB_MODE
    VERIFY_TOKEN = config.VERIFY_TOKEN

    def __init__(self, hub_mode, hub_verify_token, hub_challenge):
        self.hub_mode = hub_mode
        self.hub_verify_token = hub_verify_token
        self.hub_challenge = hub_challenge

    def response(self):
        if self.hub_mode == self.HUB_MODE and (self.hub_challenge is not None):
            if not self.hub_verify_token == self.VERIFY_TOKEN:
                return "Verification token mismatch", 403
            return self.hub_challenge, 200
        return 'This is a test chatbot.'


def send_message(dict_resp):
    params = {"access_token": config.PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = json.dumps(dict_resp)
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
                      params=params,
                      headers=headers,
                      data=data)


class ResponseObject(object):
    def __init__(self, sender, single_response, response_packet, last):
        self.sender = sender
        self.content = single_response.content
        self.content_type = single_response.content_type
        self.complement_info = single_response.complement_info
        self.quick_reply_id = response_packet.quick_reply_id if last else ""
        self.quick_reply = QuickReplier(response_packet.quick_reply_id)

    def send(self):
        send_message(self.to_dict())

    def to_dict(self):
        message = self.get_message()
        return {
            "recipient": {
                "id": str(self.sender)
            },
            "message": message.to_dict()
        }

    def get_message(self):
        if self.content_type == "text":
            message = self.type_text()
        elif self.content == "image":
            message = self.type_image()
        else:
            message = None
        return message

    def type_text(self):
        return TextMessage(content=self.content, quick_reply=self.quick_reply)

    def type_image(self):
        return ImageMessage(content=self.content, quick_reply=self.quick_reply)


class ResponseObjectPacket(object):
    def __init__(self, response_packet, message_info):
        self.response_packet = response_packet
        self.message_info = message_info

    def send_all(self):
        dict_list = []
        for ro in self.list():
            ro.send()
            dict_list.append(ro.to_dict())
        return dict_list

    def list(self):
        counter = 1
        packet = []
        for single_response in self.response_packet.single_responses:
            ro = ResponseObject(
                sender=self.message_info.sender,
                single_response=single_response,
                response_packet=self.response_packet,
                last=counter == len(self.response_packet.single_responses)
            )
            packet.append(ro)
        return packet


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
        for rop in self.responses:
            messages.append(rop.send_all())
        return messages

    def get_responses(self):
        for message in self.message_postback_list:
            message_info = MessageInfo(message)
            response_packet = ConversationAgent(message_info).get_responses()
            ROP = ResponseObjectPacket(response_packet, message_info)
            self.responses.append(ROP)


# Conversation Agent

class ConversationAgent(object):

    def __init__(self, message_info):
        self.text = message_info.text
        self.payload = message_info.payload
        self.attachments = message_info.attachments
        self.sender = message_info.sender
        self.responses = None

    def get_responses(self):
        response_packet = None
        if self.payload:
            response_packet = PayloadResponses(self.payload).generate()
        elif self.attachments:
            response_packet = AttachmentResponses(self.attachments).generate()
        elif self.text:
            response_packet = TextResponses(self.text).generate()
        else:
            response_packet = AnythingElseResponses().generate()
        return response_packet

# Respond Anything

class AnythingElseResponses(object):

    def __init__(self, something=None):
        self.something = something
        self.response_packet = None

    def generate(self):
        self.random_answer()
        return self.response_packet

    def random_answer(self):
        self.response_packet = ResponsePacket(
            quick_reply_id="main_menu",
            single_list=[
                SingleResponse(
                    content="Whoa!",
                    content_type="text",
                    complement_info="None"
                ),
                SingleResponse(
                    content="Thanks, I guess.",
                    content_type="text",
                    complement_info="None"
                )
            ]
        )

# Attachment Responses


class AttachmentResponses(object):

    def __init__(self, attachment_dict):
        self.attachment_dict = attachment_dict
        self.response_packet = None

    def generate(self):
        self.respond_image_url()
        self.generic()
        return self.response_packet

    def respond_image_url(self):

        if "image" in str(self.attachment_dict[0]['type']):
            image_url = str(self.attachment_dict[0]['payload'].get("url"))
            #ocr_results = OCR.get_text_from_url(image_url)
            try:
                ocr_results = OCR.get_text_from_url(image_url)
            except Exception as e:
                ocr_results = None #"Error: " + str(e)

            if ocr_results is None:
                try:
                    r = urlfetch.fetch(
                        url="https://rhdzmota-cloud-storage.herokuapp.com/cloud-vision/google-dropbox-ocr",
                        headers={"Content-Type": "application/json"},
                        method='POST',
                        payload=json.dumps({
                            "file_url": image_url
                        }))
                    try:
                        ocr_results = str(json.loads(r.content))
                    except Exception:
                        ocr_results = str(r.content)

                    ocr_results = ocr_results.split("text': u'")[-1]\
                        .replace("'}", "")\
                        .replace("\\n", "\n")\
                        .replace("\\u", "") if "text" in ocr_results else ocr_results
                    ocr_results = ocr_results if len(ocr_results) > 4 else "String problems (line 223)."


                    #r = requests.post(
                    #    url="https://rhdzmota-cloud-storage.herokuapp.com/cloud-vision/google-dropbox-ocr",
                    #    headers={"Content-Type": "application/json"},
                    #    data=json.dumps({
                    #        "file_url": image_url
                    #    }),
                    #    timeout=5
                    #)
                    #ocr_results = str(r.json().get("text"))
                except requests.exceptions.ConnectionError:
                        ocr_results = "Connection Error. Your photo: " + image_url
                except Exception as e:
                    #ocr_results = "Unknown Error. But hey, this url takes you to your photo: " + image_url
                    ocr_results = str(e)

            self.response_packet = ResponsePacket(
                quick_reply_id="main_menu",
                single_list=[
                    SingleResponse(
                        content=ocr_results,
                        content_type="text",
                        complement_info="None"
                    )
                ]
            )

    def generic(self):
        if self.response_packet is None:
            self.response_packet = ResponsePacket(
                quick_reply_id="main_menu",
                single_list=[
                    SingleResponse(
                        content="Nice " + str(self.attachment_dict[0]['type']),
                        content_type="text",
                        complement_info="None"
                    )
                ]
            )

# Generate Payload Reponses

class PayloadResponses(object):

    def __init__(self, payload):
        self.payload = payload
        self.response_packet = None

    def generate(self):
        self.main_menu()
        self.more_options()
        self.op1()
        self.op2()
        self.generic()
        return self.response_packet

    def generic(self):
        if self.response_packet is None:
            self.response_packet = ResponsePacket(
                quick_reply_id="main_menu",
                single_list=[
                    SingleResponse(
                        content="This is a response for a generic payload",
                        content_type="text",
                        complement_info="None"
                    )
                ]
            )

    def main_menu(self):
        if self.payload == "Hello":
            self.response_packet = ResponsePacket(
                quick_reply_id="main_menu",
                single_list=[
                    SingleResponse(
                        content="Hello to you.",
                        content_type="text",
                        complement_info="None"
                    ),
                    SingleResponse(
                        content="Again",
                        content_type="text",
                        complement_info="None"
                    )
                ]
            )

    def more_options(self):
        if self.payload == "more_options":
            self.response_packet = ResponsePacket(
                quick_reply_id="more_options",
                single_list=[
                    SingleResponse(
                        content="There you go.",
                        content_type="text",
                        complement_info="None"
                    )
                ]
            )

    def op1(self):
        if self.payload == "OP1":
            self.response_packet = ResponsePacket(
                quick_reply_id="main_menu",
                single_list=[
                    SingleResponse(
                        content="You selected option 1.",
                        content_type="text",
                        complement_info="None"
                    )
                ]
            )

    def op2(self):
        if self.payload == "OP2":
            self.response_packet = ResponsePacket(
                quick_reply_id="main_menu",
                single_list=[
                    SingleResponse(
                        content="You selected option 2.",
                        content_type="text",
                        complement_info="None"
                    )
                ]
            )


# Text Responses
class TextResponses(object):

    def __init__(self, text):
        self.text = text
        self.response_packet = None

    def generate(self):
        self.hello_world()
        self.accept()
        #self.trip_example()
        self.generic()
        return self.response_packet

    def hello_world(self):
        if "hello" in self.text.lower():
            self.response_packet = ResponsePacket(
                quick_reply_id="main_menu",
                single_list=[
                    SingleResponse(
                        content="hey :)",
                        content_type="text",
                        complement_info="None"
                    ),
                    SingleResponse(
                        content="look!",
                        content_type="text",
                        complement_info="None"
                    )
                ]
            )

    def generic(self):
        def repeat_text(text):
            try:
                out = "Did you said {}?".format(text)
            except UnicodeEncodeError:
                out = "Whoa! Nice one. ;)"
            return out

        if self.response_packet is None:
            self.response_packet = ResponsePacket(
                quick_reply_id="main_menu",
                single_list=[
                    SingleResponse(
                        content=repeat_text(self.text),
                        content_type="text",
                        complement_info="None"
                    )
                ]
            )

    def accept(self):
        if ("yes" in self.text.lower()) or ("si" in self.text.lower()):
            self.response_packet = ResponsePacket(
                quick_reply_id="main_menu",
                single_list=[
                    SingleResponse(
                        content="Great!",
                        content_type="text",
                        complement_info="None"
                    )
                ]
            )


# Generate Quick Replies

class QuickReplier(object):
    def __init__(self, quick_reply):
        self.response = None
        self.reply_type = quick_reply

    def to_dict(self):
        self.generate_quick_reply()
        return self.response.to_dict()

    def generate_quick_reply(self):
        self.more_options()
        self.main_menu()

    def more_options(self):
        if self.reply_type == "more_options":
            self.response = QuickReply(list_quick_objects=[
                QuickText(title="Option 1", payload="OP1", content_type="text"),
                QuickText(title="Option 2", payload="OP2", content_type="text")
            ])

    def main_menu(self):
        if (self.reply_type == "main_menu") or (self.response is None):
            self.response = QuickReply(list_quick_objects=[
                QuickText(title="Say Hello", payload="Hello", content_type="text"),
                QuickText(title="More opts", payload="more_options", content_type="text")
            ])
