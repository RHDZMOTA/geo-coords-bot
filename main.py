from flask import Flask, request, jsonify
from util import EntryManager
import config


app = Flask(__name__)


@app.route('/', methods=['GET'])
def get_index():
    return 'Hey there.'


@app.route('/print', methods=['POST'])
def print_post():
    data = request.get_json()
    print str(data)
    return jsonify(data)


@app.route('/bot', methods=['GET'])
def identify_fb_messenger():
    print request.args.get("hub.mode")
    print request.args.get("hub.verify_token")
    print request.args["hub.challenge"]
    if request.args.get("hub.mode") == config.HUB_MODE and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == config.VERIFY_TOKEN:
            return "Verification token mismatch", 403
        return request.args.get("hub.challenge"), 200
    return 'Hey there.'


@app.route('/bot', methods=['POST'])
def post_web_hook():
    data = request.get_json()
    print str(data)
    if data["object"] == "page":
        messages_list = []
        for entry in data["entry"]:
            print "\n\n"
            messages = EntryManager(entry).send_messages()
            messages_list.append(messages)
    return str(messages), 200


if __name__ == '__main__':
    app.run()
