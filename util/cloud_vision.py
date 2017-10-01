from settings import config
from dropbox_api import DropBoxFileManager
import base64
import json
import requests
#import requests_toolbelt.adapters.appengine

#requests_toolbelt.adapters.appengine.monkeypatch()
VISION_URL = "https://vision.googleapis.com/v1/images:annotate?key=" + config.VISION_KEY


class OCR(object):

    @staticmethod
    def get_text_from_file(file_name):
        with open(file_name, "rb") as file:
            contents = file.read()
        return OCR.get_text_from_bytes(contents)

    @staticmethod
    def get_text_from_bytes(file_bytes):
        r = requests.post(
            url=VISION_URL,
            data=OCR.base64_request_data(file_bytes),
            headers={'content-type': 'application/json'}
        )
        return OCR.extract_text(r)

    @staticmethod
    def get_text_from_url(file_url, user="temp"):
        DFM = DropBoxFileManager(user, file_url)
        DFM.upload_url_file()
        new_url = DFM.get_temporal_url()
        r = requests.post(
            url=VISION_URL,
            data=OCR.url_request_data(new_url),
            headers={'content-type': 'application/json'}
        )
        return OCR.extract_text(r)

    @staticmethod
    def extract_text(response):
        response.raise_for_status()
        return str(response.json()["responses"][0]["fullTextAnnotation"]['text'])

    @staticmethod
    def base64_request_data(file_bytes):
        return json.dumps(
            {
                "requests": [
                    {
                        "image": {
                            "content": base64.b64encode(file_bytes).decode("utf-8")
                        },
                        "features": [
                            {
                                "type": "TEXT_DETECTION"
                            }
                        ]
                    }
                ]
            }
        )

    @staticmethod
    def url_request_data(file_url):
        return json.dumps(
            {
                "requests": [
                    {
                        "image": {
                            "source": {
                                "imageUri": file_url
                            }
                        },
                        "features": [
                            {
                                "type": "TEXT_DETECTION"
                            }
                        ]
                    }
                ]
            }
        )

