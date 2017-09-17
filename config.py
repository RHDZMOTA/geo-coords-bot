import os
import json


with open('client_secret.json') as secret_content:
    client_secrets_map = json.load(secret_content)

FB_MESSENGER = "fb-messenger"
HUB_MODE = str(client_secrets_map[FB_MESSENGER].get('hub.mode'))
VERIFY_TOKEN = str(client_secrets_map[FB_MESSENGER].get('hub.verify_token'))
PAGE_ACCESS_TOKEN = str(client_secrets_map[FB_MESSENGER].get('access_token'))
