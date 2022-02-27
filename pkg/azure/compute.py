# Import the needed management objects from the libraries. The azure.common library
# is installed automatically with the other libraries.
from azure.common.client_factory import get_client_from_cli_profile
from azure.mgmt.compute import ComputeManagementClient
from model.project import *
from model.blueprint import *
from model.disk import *
from utils.dbconn import *
from azure.common.credentials import ServicePrincipalCredentials
from utils.logger import *
from azure.mgmt.compute.models import DiskCreateOptionTypes


def create_vm_worker(rg_name, vm_name, location, username, password, vm_type, nic_id, subscription_id, image_name, project, data_disks):
    con = create_db_con()
    client_id = Project.objects(name=project)[0]['client_id']
    secret = Project.objects(name=project)[0]['secret']
    tenant_id = Project.objects(name=project)[0]['tenant_id']
    subscription_id = Project.objects(name=project)[0]['subscription_id']
    creds = ServicePrincipalCredentials(client_id=client_id, secret=secret, tenant=tenant_id)
    compute_client = ComputeManagementClient(creds,subscription_id)
    con.close()
    managed_disks = []

    lun=1
    for disk in data_disks:
        disk_client = compute_client.disks.get(rg_name, disk)
        managed_disks.append({
            'lun': lun, 
            'name': disk_client.name,
            'create_option': DiskCreateOptionTypes.attach,
            'managed_disk': {
                'id': disk_client.id
            }
        })
        lun = lun + 1
        
    
    print(
        "Provisioning virtual machine {vm_name}; this operation might take a few minutes.")
    print(nic_id)

    poller = compute_client.virtual_machines.create_or_update(rg_name, vm_name,
                                                              {
                                                                  "location": location,
                                                                  "storage_profile": {
                                                                      "data_disks": managed_disks,
                                                                      "image_reference": {
                                                                          'id': '/subscriptions/' + subscription_id + '/resourceGroups/' + rg_name + '/providers/Microsoft.Compute/images/'+image_name
                                                                      }
                                                                  },
                                                                  "hardware_profile": {
                                                                      "vm_size": vm_type
                                                                  },
                                                                  "os_profile": {
                                                                      "computer_name": vm_name,
                                                                      "admin_username": username,
                                                                      "admin_password": password
                                                                  },
                                                                  "network_profile": {
                                                                      "network_interfaces": [{
                                                                          "id": nic_id,
                                                                      }]
                                                                  }
                                                              }
                                                              )

    vm_result = poller.result()
    print("Provisioned virtual machine")
    try:
        con = create_db_con()
        BluePrint.objects(project=project, host=vm_name).update(vm_id=vm_result.name,status='100')
    except Exception as e:
        BluePrint.objects(project=project, host=vm_name).update(vm_id=vm_result.name,status='-100')
        print("VM creation updation failed: "+repr(e))
        logger("VM creation updation failed: "+repr(e),"warning")
    finally:
        con.close()


async def create_vm(project, hostname):
    con = create_db_con()
    rg_name = Project.objects(name=project)[0]['resource_group']
    location = Project.objects(name=project)[0]['location']
    subscription_id = Project.objects(name=project)[0]['subscription_id']
    username = "xmigrate"
    password = "Xmigrate@321"
    machines = BluePrint.objects(project=project, host=hostname)
    for machine in machines:
        disks = Disk.objects(project=project, host=machine['host'])
        data_disks = []
        image_name = ''
        for disk in disks:
            if disk['mnt_path'] == 'slash':
                image_name = disk['disk_id']
            else:
                data_disks.append(disk['disk_id'])
        vm_name = machine['host']
        vm_type = machine['machine_type']
        nic_id = machine['nic_id']
        
        create_vm_worker(rg_name, vm_name, location, username, password, vm_type, nic_id, subscription_id, image_name, project, data_disks)
    con.close()


def list_available_vm_sizes(compute_client, region = 'EastUS2', minimum_cores = 1, minimum_memory_MB = 768):
    vm_sizes_list = compute_client.virtual_machine_sizes.list(location=region)
    machine_types = []
    for vm_size in vm_sizes_list:
        if vm_size.number_of_cores >= int(minimum_cores) and vm_size.memory_in_mb >= int(minimum_memory_MB): 
            machine_types.append({"vm_name":vm_size.name, "cores":vm_size.number_of_cores, "osdisk":vm_size.os_disk_size_in_mb, "disk":vm_size.resource_disk_size_in_mb, "memory":vm_size.memory_in_mb, "max_data_disk":vm_size.max_data_disk_count})
    return machine_types


def get_vm_types(project):
    client = ''
    location = ''
    machine_types = []
    try:
        con = create_db_con()
        subscription_id = Project.objects(name=project)[0]['subscription_id']
        client_id = Project.objects(name=project)[0]['client_id']
        tenant_id = Project.objects(name=project)[0]['tenant_id']
        secret_id = Project.objects(name=project)[0]['secret']
        location = Project.objects(name=project)[0]['location']
        creds = ServicePrincipalCredentials(client_id=client_id, secret=secret_id, tenant=tenant_id)
        client = ComputeManagementClient(creds, subscription_id)
        machine_types = list_available_vm_sizes(client, region = location, minimum_cores = 1, minimum_memory_MB = 768)
        flag = True
    except Exception as e:
        print(repr(e))
        logger("Fetching vm details failed: "+repr(e),"warning")
        flag = False
    con.close()
    return machine_types, flag


                
            