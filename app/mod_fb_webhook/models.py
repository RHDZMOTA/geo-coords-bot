from util.base_model import SerializableModel, db
import json

# Examples

class ExampleModel2(SerializableModel):
    name = db.StringProperty(required=True)
    created_at = db.DateTimeProperty(auto_now_add=True)


class ExampleModel(SerializableModel):
    type = db.StringProperty(default="web_url")
    name = db.StringProperty(required=True)
    sub_model = db.ReferenceProperty(ExampleModel2)
    sub_model_list = db.ListProperty(db.Key)
    created_at = db.DateTimeProperty(auto_now_add=True)
    @property
    def sub_models(self):
        return [ExampleModel2.get_by_key_name(sub) for sub in self.sub_model_list]

# Buttons

class UrlButton(SerializableModel):
    type = db.StringProperty(default="web_url")
    title = db.StringProperty(required=True)
    url = db.StringProperty(required=True)


class PostbackButton(SerializableModel):
    type = db.StringProperty(default="postback")
    title = db.StringProperty(required=True)
    payload = db.StringProperty(required=True)


# Single Response

class SingleResponse(SerializableModel):
    content = db.StringProperty(required=True)
    content_type = db.StringProperty(required=True)
    complement_info = db.StringProperty(required=True)


class ResponsePacket(object):
    def __init__(self, single_list, quick_reply_id):
        self.single_responses = single_list
        self.quick_reply_id = quick_reply_id


class TextMessage(object):
    def __init__(self, content, quick_reply):
        self.content = content
        self.quick_replies = quick_reply

    def to_dict(self):
        return {
            "text": self.content,
            "quick_replies": self.quick_replies.to_dict()
        }


class ImageMessage(object):
    def __init__(self, content, quick_reply):
        self.content = content
        self.quick_replies = quick_reply

    def to_dict(self):
        return {
            "attachment": {
                "type": "image",
                "payload": {
                    "url": self.content,
                    "is_reusable": False
                }
            },
            "quick_replies": self.quick_replies.to_dict()
        }


# Entry Manager

class MessageInfo(object):
    def __init__(self, message_element):
        self.sender = message_element['sender'].get('id')
        self.text = message_element['message'].get('text')
        self.payload = None if not message_element['message'].get('quick_reply') else message_element['message']['quick_reply']['payload']
        self.attachments = message_element['message'].get('attachments')


# Quick Replier Related Models

class QuickText(SerializableModel):
    content_type = db.StringProperty(default="text")
    title = db.StringProperty(required=True)
    payload = db.StringProperty(required=True)


class QuickReply(object):

    def __init__(self, list_quick_objects):
        self.list = list_quick_objects
        self.to_dict_list = []

    def to_dict(self):
        to_dict_list = []
        for element in self.list:
            to_dict_list.append(element.build().to_dict())
        self.to_dict_list = to_dict_list
        return to_dict_list


