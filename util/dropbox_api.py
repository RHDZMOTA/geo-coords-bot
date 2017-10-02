import requests
import json
from google.appengine.api import urlfetch

urlfetch.set_default_fetch_deadline(60)


class DropBoxFileManager(object):

    upload_url = "https://rhdzmota-cloud-storage.herokuapp.com/upload-file/dropbox"
    download_url = "https://rhdzmota-cloud-storage.herokuapp.com/temporal-link/dropbox-files"
    base_dir = "/coordbot-media"

    def __init__(self, user, file_url):
        self.user = user
        self.file_url = file_url
        self.file_name = self.user + "-image-" + self.next_index() + ".png"

    def upload_url_file(self):
        response = requests.get(
            url=self.upload_url,
            params={
                "file_name": self.file_name,
                "file_url": self.file_url,
                "upload_file_path": self.base_dir
            }
        )
        #response = urlfetch.fetch(
        #    url=self.upload_url+"?file_name="+self.file_name+"&file_url="+self.file_url+"&upload_file_path="+self.base_dir
        #) #json.loads(r.content)
        #print (str(response.content))

    def get_temporal_url(self):
        response = requests.get(
            url=self.download_url,
            params={
                "file_name": self.file_name,
                "file_path": self.base_dir
            }
        )
        #response = urlfetch.fetch(
        #    url=self.download_url + "?file_name=" + self.file_name + "&file_path=" + self.base_dir,
        #    method=urlfetch.GET
        #)  # json.loads(r.content)
        return response.json().get("url") # eval(str(json.loads(response.content))).get("url") #

    def next_index(self):
        response = requests.get(self.download_url + self.base_dir).json()
        max_index = 0
        for file in list(response["files"]):
            user = file.split("-")[0]
            index = file.split("-")[-1].split(".")[0]
            if user == self.user:
                max_index = max_index if max_index > int(index) else int(index)
        return str(max_index + 1)
