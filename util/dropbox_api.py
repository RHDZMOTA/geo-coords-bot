import requests
import requests_toolbelt.adapters.appengine

requests_toolbelt.adapters.appengine.monkeypatch()


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

    def get_temporal_url(self):
        response = requests.get(
            url=self.download_url,
            params={
                "file_name": self.file_name,
                "file_path": self.base_dir
            }
        )
        return response.json().get("url")

    def next_index(self):
        response = requests.get(self.download_url + self.base_dir).json()
        max_index = 0
        for file in list(response["files"]):
            user = file.split("-")[0]
            index = file.split("-")[-1].split(".")[0]
            if user == self.user:
                max_index = max_index if max_index > int(index) else int(index)
        return str(max_index + 1)
