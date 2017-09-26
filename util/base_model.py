from flask import jsonify
from google.appengine.ext import db


class SerializableModel(db.Model):

    def to_dict(self):
        data_as_dict = {}
        for key, prop in self.properties().iteritems():
            value = getattr(self, key)
            if isinstance(value, SerializableModel):
                data_as_dict[key] = value.to_dict()
            else:
                data_as_dict[key] = str(value)
        return data_as_dict

    def jsonify(self):
        return jsonify(self.to_dict())

    def build(self):
        self.put()
        return self
