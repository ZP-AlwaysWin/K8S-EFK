import os
import json

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
                for node_ip in node_ips:
                    node_flag = 0
                    for k8s_node in k8s_nodes:
                        k8s_node = k8s_node.replace("\n", "")
                        if k8s_node == node_ip:
                            node_flag = 1
                            break;
                    if node_flag == 0:
                        print(node_ip + " is illegal")
                        return 1
                return 0
        else:
            print("Please input IPs to install.")
            return 1
    else:
        print("Please input elasticsearch's configuration.")
        return 1
    storage = get_json(data, "storage")
    if storage:
        size = get_json(storage, "size")
        if size:
            try:
                if (int(size) < 1):
                    print("Illegal storage size.")
                    return 1
            except:
                print("Illegal storage size.")
                return 1
            return 0
    else:
        print("Please set storage size")
            
def check_scale(path):
    data = get_conf(path)
    storage = get_json(data, "storage")
    scale_data = get_json(data, "scale")
    if scale_data:
        new_ips = get_json(scale_data, "new_ips")
        if new_ips:
            es_nodes = os.popen("/root/local/bin/kubectl get po -o wide| grep elasticsearch | awk '{print $7}'").readlines()
            for new_ip in new_ips:
                print("new_ip:" + new_ip)
                node_flag = 0
                for es_node in es_nodes:
                    es_node = es_node.replace("\n", "")
                    print(es_node)
                    if es_node == new_ip:
                        print("es_node == new_ip")
                        node_flag = 1
                        print("in " + str(node_flag))
                        break;
                if node_flag == 1:
                    print(new_ip + " is illegal")
                    return 1
                k8s_nodes = os.popen("/root/local/bin/kubectl get node | grep Ready | awk '{print $1}'").readlines()
                for new_ip in new_ips:
                    node_flag = 0
                    for k8s_node in k8s_nodes:
                        k8s_node = k8s_node.replace("\n", "")
                        print("k8s   " + k8s_node)
                        if k8s_node == new_ip:
                            print("k8s_node == new_ip")
                            node_flag = 1
                            break;
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

