#encoding=utf-8
import os
import utils

config_path = "/config/es.json"
dir = os.path.split(os.path.realpath(__file__))[0]

def get_new_node():
    data = utils.get_conf(dir + config_path)
    scale_data = data["scale"]
    new_ips = scale_data["new_ips"]
    new_len = len(new_ips)
    new_str = ""
    count = 0
    for new_ip in new_ips:
        count += 1
        new_str = new_str + '"' + new_ip + '",'
        os.system("/root/local/bin/kubectl label node " + new_ip + " es=elasticsearch --overwrite=true 2>&1")
    es_data = data["elasticsearch"]
    node_ips = es_data["node_ips"]
    node_str = ""
    for node_ip in node_ips:
        count += 1
        ip = '"' + node_ip + '"' 
        node_str = node_str + ip + ","
    all_str = node_str + new_str
    print("all_str:" + str(all_str))
    
    es_lines = []
    es_yml = open(dir + "/configmap/elasticsearch-template.yml", "r")
    for line in es_yml:
        if "[CLUSTER_IP]" in line:
            line = line.replace("CLUSTER_IP", all_str)
        es_lines.append(line)
    es_yml.close()
    es_join = "".join(es_lines)
    elasticsearch_yml = open(dir + "/configmap/elasticsearch.yml", "w+")
    elasticsearch_yml.write(es_join)
    elasticsearch_yml.close()
    
    os.system("/root/local/bin/kubectl delete configmap es-configmap")
    os.system("/root/local/bin/kubectl create configmap es-configmap --from-file=" + dir + "/configmap/")
    print("count:" + str(count))	
    return count

def scale_cluster():
    if utils.check_scale(dir + config_path) == 1:
        return 1
    replicas = get_new_node()
    os.system("/root/local/bin/kubectl scale sts elasticsearch --namespace=kube-efk --replicas=" + str(replicas))

if __name__ == '__main__':
    try:
        scale_cluster()
    except:
        print("Scale failed")
    #get_new_node()
