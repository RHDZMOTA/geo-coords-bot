from settings import config
import requests
import json


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
                    content=element["responses"][i]["content"],
                    content_type=element["responses"][i]["content-type"],
                    quick_reply_id="" if i != n_responses else element["quick_reply"],
                    complement_info=element["responses"][i]["complement-info"]
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


