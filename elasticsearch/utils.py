import os
import re
import json
from ...k8s.rbd import have_disk
from ...k8s.rbd import get_size_need

config_path = "/config/es.json"
dir = os.path.split(os.path.realpath(__file__))[0]

def get_conf(path):
    try:
        fo = open(path, 'r')
        data = json.load(fo)
        fo.close()
        return data
    except:
        print("Illegal configuration file.")
        return 1

def get_json(obj, key):
    if(key in obj):
        return obj[key]
    else:
        print("Wrong configuration with " + key + "!")
        return False

def check_json(obj, key):
    if (key in obj):
        return True
    else:
        return False

def check_disk():
    path = dir + "/config/es.json"
    data = get_conf(path)
    node_ips= data["elasticsearch"]["node_ips"]
    host_path = data["storage"]["hostPath"]
    if str(host_path) == "true":
        return 0
    replicas = len(node_ips)
    storage_size = data["storage"]["size"]
    volumes = []
    volume = {'num':int(replicas), 'size':int(storage_size)}
    volumes.append(volume)
    total_size = get_size_need(volumes)
    print(total_size)
    return total_size

def get_disk():
    need_size = check_disk()
    result = have_disk(need_size)
    if(result == 0):
        print("Disk is enough to install elasticsearch")
        return 0
    else:
        print("Disk is not enough to install elasticsearch")
        return 1


def check_install(path):
    data = get_conf(path)
    elasticsearch_data = get_json(data, "elasticsearch")
    if elasticsearch_data:
        node_ips = get_json(elasticsearch_data, "node_ips")
        if node_ips:
            if not isinstance(node_ips, list):
                print("Please input list of IP.")
                return 1
            else:
                k8s_nodes = os.popen("/root/local/bin/kubectl get node | grep Ready | awk '{print $1}'").readlines()
                es_nodes = []
                for node_ip in node_ips:
                    if node_ip not in es_nodes:
                        es_nodes.append(node_ip)
                    else:
                        print("Repeated IP: " + str(node_ip))
                        return 1
                    node_flag = 0
                    for k8s_node in k8s_nodes:
                        k8s_node = k8s_node.replace("\n", "")
                        if k8s_node == node_ip:
                            node_flag = 1
                            break;
                    if node_flag == 0:
                        print(node_ip + " is illegal")
                        return 1
        else:
            print("Please input IPs to install.")
            return 1
    else:
        print("Please input elasticsearch's configuration.")
        return 1
    storage = get_json(data, "storage")
    if storage:
        hostPath = get_json(storage, "hostPath")
        pathDir = get_json(storage, "pathDir")
        if hostPath:
            if hostPath == "false":
                size = get_json(storage, "size")
                print("test size:" + str(size))
                if size:
                    try:
                        if (int(size) < 1):
                            print("Illegal storage size.")
                            return 1
                    except:
                        print("Illegal storage size.")
                        return 1
                    if get_disk() == 0:
                        return 0
                    else:
                        return 1
                else:
                    print("Please set storage size.")
                    return 1
            elif hostPath == "true":
                pathDir = get_json(storage, "pathDir")
                if pathDir:
                    pd_res = re.match(r'\A\/', str(pathDir))
                    if not pd_res:
                        print("Please input legal dir.")
                        return 1
                else:
                    print("Please set pathDir.")
                    return 1
                return 0
        else:
            print("Please choose hostpath or not.")
            return 1
    else:
        print("Please set storage.")
        return 1
            
def check_scale(path):
    data = get_conf(path)
    storage = get_json(data, "storage")
    scale_data = get_json(data, "scale")
    if scale_data:
        new_ips = get_json(scale_data, "new_ips")
        print("new_ips:", new_ips)
        if new_ips:
            es_nodes = os.popen("/root/local/bin/kubectl get po -o wide -n kube-efk| grep elasticsearch | awk '{print $7}'").readlines()
            new_nodes = []
            for new_ip in new_ips:
                if new_ip not in new_nodes:
                    new_nodes.append(new_ip)
                else:
                    print("Repeated IP: " + str(new_ip))
                    return 1
                print("new_ip:" + new_ip)
                node_flag = 0
                for es_node in es_nodes:
                    es_node = es_node.replace("\n", "")
                    print(es_node)
                    if es_node == new_ip:
                        print("Repeated IP!")
                        node_flag = 1
                        print("in " + str(node_flag))
                        break
                if node_flag == 1:
                    print(new_ip + " is illegal")
                    return 1
                k8s_nodes = os.popen("/root/local/bin/kubectl get node | grep Ready | awk '{print $1}'").readlines()
                for new_ip in new_ips:
                    node_flag = 0
                    for k8s_node in k8s_nodes:
                        k8s_node = k8s_node.replace("\n", "")
                        if k8s_node == new_ip:
                            print("Legal IP in node")
                            node_flag = 1
                            break
                    if node_flag == 0:
                        print(new_ip + " is illegal")
                        return 1
            return 0
        else:
            print("Please input IP to scale.")
            return 1
    else:
        print("Please input IP to scale.")
        return 1

