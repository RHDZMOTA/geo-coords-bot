from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for, jsonify
from werkzeug import check_password_hash, generate_password_hash
from app import app
from app.mod_fb_webhook.models import ExampleModel, ExampleModel2

from util.util import EntryManager
from app.mod_fb_webhook.services import FacebookWebHook
import settings.config as config


mod_fb_webhook = Blueprint('fb-webhook', __name__, url_prefix='/fb-webhook')


@mod_fb_webhook.route('/test-model/<name>', methods=['GET'])
def test_model(name=""):
    m1 = ExampleModel2(name=name).build()
    model = ExampleModel(
        name=name,
        sub_model=m1).build()
    return model.jsonify()


@mod_fb_webhook.route('/geo-coords-bot', methods=['GET'])
def identify_fb_messenger():
    return FacebookWebHook(
        hub_mode=request.args.get("hub.mode"),
        hub_verify_token=request.args.get("hub.verify_token"),
        hub_challenge=request.args.get("hub.challenge")).response()


@mod_fb_webhook.route('/geo-coords-bot', methods=['POST'])
def post_web_hook():
    data = request.get_json()
    messages_list = []
    if data.get("object") == "page":
        for entry in data["entry"]:
            messages = EntryManager(entry).send_messages()
            messages_list.append(messages)
    return jsonify({"message_list": messages_list}), 200

