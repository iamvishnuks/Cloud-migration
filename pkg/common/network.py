from utils.dbconn import *
from utils.converter import *
from model.discover import *
from model.blueprint import *
from model.project import *
from model.network import *
import json
from collections import defaultdict
import traceback

def update_nw_cidr(p):
    machines = json.loads(Discover.objects(project=p).allow_filtering())
    networks = []
    print("trying to update network")
    for machine in machines:
        networks.append(machine['network'])
    network_count = len(list(set(networks)))
    networks = list(set(networks))
    vpc_cidr = defaultdict(list)
    subnet_machines = defaultdict(list)
    vpcs = defaultdict(list)
    for i in machines:
        vpc_cidr[i['network']].append(i['subnet'])
    for i in vpc_cidr.keys():
        subnet_prefixes = []
        subnet_prefix = 0
        for j in vpc_cidr[i]:
            subnet_prefixes.append(int(j.split('/')[-1]))
            subnet_prefix = min(subnet_prefixes)
            vp = i+'/'+str(subnet_prefix-2)
            if '/' not in i:
                try:
                    con = create_db_con()
                    Discover.objects(network=i,project=p).update(network=vp)
                    print(Discover.objects.allow_filtering())
                except:
                    print("Failed upating network")
                finally:
                    con.shutdown()
    return True


def update_subnet(cidr,p):
    con = create_db_con()
    print("trying t update subnet")
    machines = json.loads(Discover.objects(project=p).allow_filtering())
    if cidr == '10.0.0.0':
        for machine in machines:
            if machine['network'].split('.')[0] == '10':
                continue
            machine['ip'] = machine['ip'].split('.')
            machine['ip'][0] = '10'
            machine['ip'] = '.'.join(machine['ip'])
            machine['network'] = machine['network'].split('.')
            machine['network'][0] = '10'
            machine['network'] = '.'.join(machine['network'])
            machine['subnet'] = machine['subnet'].split('.')
            machine['subnet'][0] = '10'
            machine['subnet'] = '.'.join(machine['subnet'])
           # print machine
    elif cidr == '172.16.0.0':
        for machine in machines:
            if machine['network'].split('.')[0] == '172':
                continue
            machine['ip'] = machine['ip'].split('.')
            machine['ip'][0] = '172'
            machine['ip'][1] = '16'
            machine['ip'] = '.'.join(machine['ip'])
            machine['network'] = machine['network'].split('.')
            machine['network'][0] = '172'
            machine['network'][1] = '16'
            machine['network'] = '.'.join(machine['network'])
            machine['subnet'] = machine['subnet'].split('.')
            machine['subnet'][0] = '172'
            machine['subnet'][1] = '16'
            machine['subnet'] = '.'.join(machine['subnet'])
            # print machine
    elif cidr == '192.168.0.0':
        for machine in machines:
            if machine['network'].split('.')[0] == '192':
                continue
            machine['ip'] = machine['ip'].split('.')
            machine['ip'][0] = '192'
            machine['ip'][1] = '168'
            machine['ip'] = '.'.join(machine['ip'])
            machine['network'] = machine['network'].split('.')
            machine['network'][0] = '192'
            machine['network'][1] = '168'
            machine['network'] = '.'.join(machine['network'])
            machine['subnet'] = machine['subnet'].split('.')
            machine['subnet'][0] = '192'
            machine['subnet'][1] = '168'
            machine['subnet'] = '.'.join(machine['subnet'])
            # print machine
    else:
        return machines, False
    con.shutdown()
    return machines, True


def update_blueprint(machines,p):
    con = create_db_con()
    for machine in machines:
        ram = conv_KB(machine['ram'].split(' ')[0])
        machine['machine_type'] = ''#compu( machine_type, int(machine['cores']), ram)
        post = BluePrint(host=machine['host'], ip=machine['ip'], subnet=machine['subnet'], network=machine['network'], project=p,
                         ports=machine['ports'], cores=machine['cores'], public_route=True, cpu_model=machine['cpu_model'], ram=machine['ram'], machine_type='', status='Not started')
        try:
            post.save()
        except Exception as e:
            print("Boss you have to see this!!")
            print(e)
            return False
        finally:
            con.shutdown()
    return True


def create_nw_layout(cidr,p):
    con = create_db_con()
    blueprint_updated = True
    try:
        BluePrint.objects(project=p).delete()
        print("Deleted objects")
    except Exception as e:
        print("See the error:" + str(e))
    network_cidr_updated = update_nw_cidr(p)
    if network_cidr_updated:
        machines, subnet_updated = update_subnet(cidr,p)
        if subnet_updated:
            blueprint_updated = update_blueprint(machines,p)
        else:
            print("subnet not updated")
            return subnet_updated
    return blueprint_updated


def create_nw(project,name,cidr):
    con = create_db_con()
    provider = Project.objects(name=project).allow_filtering()[0]['provider']
    try:
        if provider == 'gcp':
            Network(project=project,nw_name=name).save()
        else:
            Network(project=project,nw_name=name,cidr=cidr).save()
        return True
    except Exception as e:
        print(str(e))
        return False
    finally:
         con.shutdown()

def delete_nw(project,name):
    con = create_db_con()
    try:
        Network.objects(project=project,nw_name=name).delete()
        subnets = Subnet.objects(project=project,nw_name=name).allow_filtering()
        for subnet in subnets:
            Subnet.objects(project=project,subnet_name=subnet['subnet_name'], cidr=subnet['cidr']).delete()
        con.shutdown()
        return True
    except Exception as e:
        print(str(e))
        con.shutdown()
        return False

def delete_subnet(project,name, nw_name):
    con = create_db_con()
    try:
        cidr = Subnet.objects(project=project,subnet_name=name).allow_filtering()[0]['cidr']
        Subnet.objects(project=project,subnet_name=name,cidr=cidr).delete()
        con.shutdown()
        return True
    except Exception as e:
        print(str(e))
        con.shutdown()
        return False


def fetch_nw(project):
    con = create_db_con()
    try:
        result = [dict(x) for x in Network.objects(project=project).allow_filtering()]
        con.shutdown()
        return result
    except Exception as e:
        con.shutdown()
        result = {"msg":"Failed to retrieve network details"}
        return result


def fetch_subnet(project,network):
    con = create_db_con()
    try:
        if network == 'all':
            result = [dict(x) for x in Subnet.objects(project=project).allow_filtering()]
        else:
            result = [dict(x) for x in Subnet.objects(project=project, nw_name=network).allow_filtering()]
        con.shutdown()
        return result
    except Exception as e:
        con.shutdown()
        result = {"msg":"Failed to retrieve network details"}
        return result


def create_subnet(cidr,nw_name,project,subnet_type,name):
    con = create_db_con()
    try:
        if subnet_type == 'Public':
            subnet_type = True
        elif subnet_type == 'Private':
            subnet_type = False
        Subnet.objects(project=project,subnet_name=name,cidr=cidr).update(nw_name=nw_name,subnet_type=subnet_type)
        if len(Subnet.objects(project=project).allow_filtering()) == 1:
            nw = Network.objects(project=project, nw_name=nw_name).allow_filtering()
            machines = Discover.objects(project=project).allow_filtering()
            for machine in machines:
                try:
                    network_cidr= nw[0]['nw_name'] if nw[0]['cidr'] == None else nw[0]['cidr']               
                    BluePrint.objects(project=project, host=machine['host']).update(ip='Not created', subnet=cidr, network=network_cidr,
                         ports=machine['ports'], cores=str(machine['cores']), public_route=subnet_type, cpu_model=machine['cpu_model'], ram=str(machine['ram']), machine_type='', status='0')
                    con.shutdown()
                except Exception as e:
                    # print(traceback.format_exc())
                    print("Error while updating BluePrint: "+repr(e))
                    con.shutdown()
            return True       
        else:
            return True
    except Exception as e:
        print("Error while updating Subnet: "+str(e))
        con.shutdown()
        return False
