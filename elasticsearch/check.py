import os

def get_status():
    pod_ip = os.popen("/root/local/bin/kubectl get po --namespace=kube-efk -o wide | grep elasticsearch-0 | awk '{print $7}'").readlines()[0]
    pod_ip = pod_ip.replace("\n", "")
    print("pod_ip" + pod_ip)
    status = os.popen("curl -uelastic:changeme http://" + pod_ip + ":9200/_cat/health?pretty | awk '{print $4}'").readlines()[0]
    status = status.replace("\n", "")
    if status == "green":
        node_num = os.popen("curl -uelastic:changeme http://" + pod_ip + ":9200/_cat/health?pretty | awk '{print $5}'").readlines()[0]
        node_num = node_num.replace("\n", "")
        desired_num = os.popen("/root/local/bin/kubectl get sts --namespace=kube-efk | grep elasticsearch | awk '{print $2}'").readlines()[0]
        desired_num = desired_num.replace("\n", "")
        if desired_num == node_num:
            return 0
        else:
            return 1
    else:
        print("not green")
        return 1

def check_cluster():
    try:
        if get_status() == 0:
            print("Elasticsearch cluster is healthy.")
            return 0
        else:
            print("Elasticsearch cluster is unhealthy.")
            return 1 
    except:
        print("Elasticsearch cluster is unhealthy.")
        return 1
		
if __name__ == '__main__':
    check_cluster()
