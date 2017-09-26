from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from google.appengine.ext import db

app = Flask(__name__)
app.config.from_object('app_config')
#db = SQLAlchemy(app)

# FB-Webhook
from app.mod_fb_webhook.controllers import mod_fb_webhook as fb_webhook
app.register_blueprint(fb_webhook)

#db.create_all()
