# geo-coords-bot

FB-Messenger Bot. 

@author: [@rhdzmota](rhdzmota@mxquants.com)

## Setup

1. Create a virtuale environment.
* `virtualenv -p /usr/bin/python2.7 venv`
* `source activate venv`

2. Install requirements.
* `pip install --upgrade -t lib -r requirements.txt`

3. Run setup script.
* `python setup.py`

## Usage

Using pure Flask:
* `source activate venv`
* `python run.py`

Using Google App Server:
* `source activate venv`
* `dev_appserver.py app.yaml`

Upload to production:
* `gcloud app deploy --project geo-coords-bot`

## TODO

[tbd]