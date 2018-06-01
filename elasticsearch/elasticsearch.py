#encoding=utf-8
import os
import utils

config_path = "/config/es.json"
dir = os.path.split(os.path.realpath(__file__))[0]

def produce_yaml():
    data = utils.get_conf(dir + config_path)
    es_data = data["elasticsearch"]
    node_ips = es_data["node_ips"]
    print("node_ips:")
    print(node_ips)
    node_str = ""
    for node_ip in node_ips:
        ip = '"' + node_ip + '"' 
        node_str = node_str + ip + ","
        print("node_str::::" + node_str)
        os.system("/root/local/bin/kubectl label node " + node_ip + " es=elasticsearch --overwrite=true 2>&1")
	
    replicas = len(node_ips)
    storage_data = data["storage"]
    size = storage_data["size"]
    es_lines = []
    es_yaml = open(dir + "/yaml/elasticsearch-template.yaml", "r")
    for line in es_yaml:
        if "replicas_num" in line:
            line = line.replace("replicas_num", str(replicas))
        elif "storage: 1Gi" in line:
            line = line.replace("1", str(size))
        es_lines.append(line)
    es_yaml.close()
    es_join = "".join(es_lines)
    elasticsearch_yaml = open(dir + "/yaml/elasticsearch.yaml", "w+")
    elasticsearch_yaml.write(es_join)
    elasticsearch_yaml.close()

    es_lines = []
    es_yml = open(dir + "/configmap/elasticsearch-template.yml", "r")
    for line in es_yml:
        if "[CLUSTER_IP]" in line:
            print("node_str: " + node_str)
            line = line.replace("CLUSTER_IP", node_str)
        es_lines.append(line)
    es_yml.close()
    es_join = "".join(es_lines)
    elasticsearch_yml = open(dir + "/configmap/elasticsearch.yml", "w+")
    elasticsearch_yml.write(es_join)
    elasticsearch_yml.close()


def create_cluster():
    produce_yaml()
    os.system("/root/local/bin/kubectl create configmap es-configmap -n kube-efk --from-file=" + dir + "/configmap/")
    os.system("/root/local/bin/kubectl create -f " + dir + "/yaml/elasticsearch.yaml")
    print("Cluster created")
    return 0

def install_elasticsearch():
    path = dir + config_path
    print("Checking config...")
    if utils.check_install(path) == 1:
        return 1
    print("=====")
    try:
        create_cluster()
        return 0
    except:
        return 1

if __name__ == '__main__':
    install_elasticsearch()
    #produce_yaml()
