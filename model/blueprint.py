from mongoengine import *

class BluePrint(Document):
    host = StringField(required=True, max_length=200, unique=True)
    ip = StringField(required=True, unique=True)
    subnet = StringField(required=True, max_length=50)
    network = StringField(required=True, max_length=50)
    ports = ListField()
    cores = StringField(max_length=2)
    cpu_model = StringField(required=True, max_length=150)
    ram = StringField(required=True, max_length=50)
    machine_type = StringField(required=True, max_length=150)
    status = StringField(required=False, max_length=100)
    image_id = StringField(required=False, max_length=100)
    vpc_id = StringField(required=False, max_length=100)
    subnet_id = StringField(required=False, max_length=200)
    public_route = StringField(required=False, max_length=10)
    ig_id = StringField(required=False, max_length=100)
    route_table = StringField(required=False, max_length=100)
    vm_id = StringField(required=False, max_length=200)
    project = StringField(required=True, max_length=50,unique=True)
    nic_id = StringField(max_length=200)

