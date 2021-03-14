from mongoengine import *

class Discover(Document):
    host = StringField(required=True, max_length=200 )
    ip = StringField(required=True, max_length=150)
    subnet = StringField(required=True, max_length=150)
    network = StringField(required=True, max_length=150)
    ports = ListField()
    cores = StringField(max_length=150)
    cpu_model = StringField(required=True, max_length=150)
    ram = StringField(required=True, max_length=150)
    disk = StringField(required=True, max_length=150)
    project = StringField(required=True, max_length=150)
    public_ip = StringField(required=True, max_length=150)
    username = StringField(required=True, max_length=150)
    password = StringField(required=True, max_length=150)
    meta = {
        'indexes': [
            {'fields': ('host', 'project'), 'unique': True}
        ]
    }

