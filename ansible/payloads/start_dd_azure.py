import os
from mongoengine import *
import socket
import sys


db_con_string = sys.argv[3]
con = connect(host=db_con_string)
url = sys.argv[1]
sas = sys.argv[2]
project = sys.argv[4]


hostname = socket.gethostname()

class Discover(Document):
    host = StringField(required=True, max_length=200 )
    ip = StringField(required=True)
    subnet = StringField(required=True, max_length=150)
    network = StringField(required=True, max_length=150)
    ports = ListField()
    cores = StringField(max_length=2)
    cpu_model = StringField(required=True, max_length=150)
    ram = StringField(required=True, max_length=150)
    disk_details = ListField()
    project = StringField(required=True, max_length=150)
    public_ip = StringField(required=True, max_length=150)
    meta = {
        'indexes': [
            {'fields': ('host', 'project'), 'unique': True}
        ]
    }


class BluePrint(Document):
    host = StringField(required=True, max_length=200)
    ip = StringField(required=True)
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
    public_route = BooleanField(required=False)
    ig_id = StringField(required=False, max_length=100)
    route_table = StringField(required=False, max_length=100)
    vm_id = StringField(required=False, max_length=200)
    project = StringField(required=True, max_length=50)
    nic_id = StringField(max_length=200)
    disk_clone = ListField()
    meta = {
        'indexes': [
            {'fields': ('host', 'project'), 'unique': True}
        ]
    }
    
disks = Discover.objects(host=hostname,project=project)[0]['disk_details']
BluePrint.objects(host=hostname,project=project).update(status='22')
output=''
disk_clone_data = []
try:
    for disk in disks:
        try:
            current_disk = {"dev":disk['dev'], "status":"10"}
            disk_clone_data.append(current_disk)
            BluePrint.objects(host=hostname,project=project).update(disk_clone=disk_clone_data)
            mnt_path = disk['mnt_path']
            mnt_path = mnt_path.replace("/","-slash")
            output = os.popen('sudo dd if='+disk["dev"]+' bs=1M status=progress | azcopy copy "'+url+hostname+mnt_path+'.raw?'+sas+'" --from-to PipeBlob').read()
            # os.system('sudo dd if='+disks[mnt]+' bs=1M status=progress | azcopy copy "'+url+hostname+mnt_path'.raw?'+sas+'" --from-to PipeBlob')
            for i in disk_clone_data:
                if i['dev']==disk['dev']:
                    i['status'] = "100"
                    i['status_msg'] = output
            BluePrint.objects(host=hostname,project=project).update(disk_clone=disk_clone_data)
        except Exception as e:
            print(str(e))
            for i in disk_clone_data:
                if i['dev']==disk['dev']:
                    i['status'] = "-1"
                    i['status_msg'] = output
            BluePrint.objects(host=hostname,project=project).update(disk_clone=disk_clone_data)
    BluePrint.objects(host=hostname, project=project).update(status='25')
except:  
    BluePrint.objects(host=hostname, project=project).update(status='-25')
finally:
    con.close()