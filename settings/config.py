import os
import json


with open('settings/client_secret.json') as secret_content:
    client_secrets_map = json.load(secret_content)

FB_MESSENGER = "fb-messenger"
HUB_MODE = client_secrets_map[FB_MESSENGER].get('hub.mode')
VERIFY_TOKEN = client_secrets_map[FB_MESSENGER].get('hub.verify_token')
PAGE_ACCESS_TOKEN = client_secrets_map[FB_MESSENGER].get('access_token')

GOOGLE = "google"
VISION_KEY = client_secrets_map[GOOGLE].get('cloud-vision')
