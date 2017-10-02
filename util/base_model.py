from flask import jsonify
from google.appengine.ext import db


class SerializableModel(db.Model):

    def to_dict(self):
        data_as_dict = {}
        for key, prop in self.properties().iteritems():
            value = getattr(self, key)
            if isinstance(value, SerializableModel):
                data_as_dict[key] = value.to_dict()
            elif isinstance(value, list):
                dict_list = []
                for element in value:
                    dict_list.append(
                        SerializableModel.get_by_id(element.id()).to_dict() if isinstance(element, db.Key) and SerializableModel.get_by_id(element.id()) is not None else str(element)
                    )
                data_as_dict[key] = str(dict_list)
            else:
                data_as_dict[key] = str(value)
        return data_as_dict

    def jsonify(self):
        return jsonify(self.to_dict())

    def build(self):
        self.put()
        return self
