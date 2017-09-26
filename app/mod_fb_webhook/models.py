from util.base_model import SerializableModel, db


# Examples

class ExampleModel2(SerializableModel):
    name = db.StringProperty(required=True)
    created_at = db.DateTimeProperty(auto_now_add=True)


class ExampleModel(SerializableModel):
    type = db.StringProperty(default="web_url")
    name = db.StringProperty(required=True)
    sub_model = db.ReferenceProperty(ExampleModel2)
    created_at = db.DateTimeProperty(auto_now_add=True)


# Buttons

class UrlButton(SerializableModel):
    type = db.StringProperty(default="web_url")
    title = db.StringProperty(required=True)
    url = db.StringProperty(required=True)


class PostbackButton(SerializableModel):
    type = db.StringProperty(default="postback")
    title = db.StringProperty(required=True)
    payload = db.StringProperty(required=True)


# Single Response

class SingleResponse(SerializableModel):
    content = db.StringProperty(required=True)
    content_type = db.StringProperty(required=True)
    complement_info = db.StringProperty(required=True)


# Quick Text

class QuickText(SerializableModel):
    content_type = db.StringProperty(default="text")
    title = db.StringProperty(required=True)
    payload = db.StringProperty(required=True)



