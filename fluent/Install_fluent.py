#encoding=utf-8

import json
import os           
import shutil
import math
import re
import logging
import sys
import time

basedir=os.path.split(os.path.realpath(__file__))[0]

logger = logging.getLogger("Install-Fluent")


formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')

fluent_log_path=basedir+"/log/Install-Fluent.log"
file_handler = logging.FileHandler(fluent_log_path)
file_handler.setFormatter(formatter) 

console_handler = logging.StreamHandler(sys.stdout)
console_handler.formatter = formatter  

logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.setLevel(logging.INFO)

def read_file (filename):
    f = open(filename)
    content = f.read()
    f.close()
    return content

def write_file (filename, text):
    f = open(filename, 'w')
    f.write(text)
    f.close()
create_n_cmd="/root/local/bin/kubectl create namespace kube-efk >/dev/null 2>&1"
exist_n_cmd="/root/local/bin/kubectl get namespace kube-efk >/dev/null 2>&1"

def create_namespace():
    return_exist_n=os.system(exist_n_cmd)
    if return_exist_n:
        print("Kubernetes Cluster Non-existent kube-efk namespaces,Whether or not to create?")
        create_input = raw_input("	y ==> create kube-efk namespace\n	n ==> don't create kube-efk namespace and exit install fluent\n")
        if create_input.strip() == "y":
            return_n_cmd=os.system(create_n_cmd)
            if return_n_cmd:
                logger.error("Creating kube-efk namespace failure")
                return 1
            else:
                logger.info("Creating kube-efk namespace success")
        elif create_input.strip() == "n":
            return 1
        else:
            print("y ==> create kube-efk namespace;\nn ==> don't create kube-efk namespace and exit install fluent\nProhibit entering other parameters,Please reinstall the input")
            return 1
def get_config(config_name):
    try:
        config = json.loads(read_file(config_name))
        hosts = []
        fluent_hosts = config['fluent_node']
        node_str = os.popen("/root/local/bin/kubectl get node|awk -F ' ' 'NR>1{print $1}'").read().strip()
        node_list = node_str.split("\n")
        for i in fluent_hosts :
            if i not in node_list:
                logger.error("The NodeIP that the user fills out does not exist in the K8S cluster")
                return 1
            if i not in hosts:
                hosts.append(i)
        if hosts:
            return [hosts]
        else:
            logger.error("Please fill in at least one IP")
            return 1
    except:
        logger.error('The Fluent config is not Json!')
        return 1

def make_labels(fluent_config):
    label_nodes = ""
    for i in fluent_config[0]:
        label_nodes += '/root/local/bin/kubectl label node {}  kubernetes-h3c/fluentd-ds-ready=true --overwrite=true >/dev/null 2>&1\n'.format(i)
    take_labels=os.popen(label_nodes).read().strip()

def check_exist_fluent():
    fluent_configmap = os.popen("/root/local/bin/kubectl get configmap -n kube-efk|grep -ci fluentd").read().strip()
    fluent_serviceaccount = os.popen("/root/local/bin/kubectl get ServiceAccount -n kube-efk|grep -ci fluentd").read().strip()
    fluent_clusterrole = os.popen("/root/local/bin/kubectl get ClusterRole -n kube-efk| grep -ci fluentd").read().strip()
    fluent_clusterrolebinding = os.popen("/root/local/bin/kubectl get ClusterRoleBinding -n kube-efk| grep -ci fluentd").read().strip()
    fluent_daemonset = os.popen("/root/local/bin/kubectl get DaemonSet -n kube-efk| grep -ci fluentd").read().strip()
    fluent_pod=os.popen("/root/local/bin/kubectl get pod -n kube-efk| grep -ci fluentd").read().strip()

    return_code = fluent_configmap+fluent_serviceaccount+fluent_clusterrole+fluent_clusterrolebinding+fluent_daemonset+fluent_pod

    if int(return_code)!=0:
        return 1
    else:
        return "not fluent"

def check_fluent_health():
    fluent_config = get_config(basedir+'/'+'fluent.json')

    if isinstance(fluent_config,int):
        return 1
    else:
        fluent_pod_num=os.popen("/root/local/bin/kubectl get pod -n kube-efk|grep -ci fluentd.*Running").read().strip()
        config_fluent_num=len(fluent_config[0])
        if int(fluent_pod_num)==int(config_fluent_num):
            logger.info("Fluent Cluster is OK!")
        else:
            logger.error("Fluent Cluster is not OK!")
            return 1

def expand_fluent():
    fluent_config = get_config(basedir+'/'+'fluent.json')

    if isinstance(fluent_config,int):
        return 1
#    else:
#        return_code=os.system("/root/local/bin/kubectl get svc elasticsearch -n kube-efk >/dev/null 2>&1")
#    if return_code!=0:
#        logger.error('The Elasticsearch Server is not exists! Forbid expanding Fluent!')
#        return 1
    else:
        exist_fluent=check_exist_fluent()

    if  isinstance(exist_fluent,str):
        logger.error("The Fluent Cluster are not exists! Forbid expanding Fluent!")
        return 1
    else:
        make_labels(fluent_config)
        logger.info("Expand fluent cluster complete! please run check_fluent_health command to expand if success!")

def delete_fluent_cluster():
    fluent_config = get_config(basedir+'/'+'fluent.json')
    exist_fluent_cluster=check_exist_fluent()
     
    if isinstance(fluent_config,int):
        return 1
    elif isinstance(exist_fluent_cluster,str):
        logger.error('The Fluent Cluster is not exists! Forbid deleteing Fluent Cluster!')
        return 1
    else:
        delete_label = ""
        logger.info("Start deleting  Fluent Cluster!")
        for i in fluent_config[0]:
            delete_label += "/root/local/bin/kubectl label node {}  kubernetes-h3c/fluentd-ds-ready- 2>/dev/null\n".format(i)
        delete_lables=os.popen(delete_label).read().strip()

        delete_args="/root/local/bin/kubectl delete daemonset fluentd-es-v0 -n kube-efk 2>/dev/null\n" \
                   + "/root/local/bin/kubectl delete configmap fluentd-es-config-v0 -n kube-efk 2>/dev/null\n"\
                   + "/root/local/bin/kubectl delete ServiceAccount fluentd-es -n kube-efk 2>/dev/null\n" \
                   + "/root/local/bin/kubectl delete ClusterRole fluentd-es -n kube-efk 2>/dev/null\n" \
                   + "/root/local/bin/kubectl delete ClusterRoleBinding fluentd-es -n kube-efk 2>/dev/null"
        delete_args=os.popen(delete_args).read().strip()
        time.sleep(6)
        logger.info("Delete Fluent Cluster")
    

def install_fluent():
    fluent_config = get_config(basedir+'/'+'fluent.json')

    if isinstance(fluent_config,int):
        return 1
 #   else:
 #       return_code=os.system("/root/local/bin/kubectl get svc elasticsearch -n kube-efk >/dev/null 2>&1")
#
 #   if return_code!=0:
  #      logger.error('The Elasticsearch Server is not exists! Forbid installing Fluent!')
  #      return 1
    else:
	    return_create_n=create_namespace()
    if return_create_n:
        return 1
    else:
        exist_fluent_cluster=check_exist_fluent()
    if isinstance(exist_fluent_cluster,int):
        logger.error("Fluent cluster already exists, please do not repeat the installation")
        return 1
    else:
        logger.info("Node IP that needs to collect logs is {}".format(fluent_config[0]))
        logger.info("Start labeling node")
        make_labels(fluent_config)

        logger.info("Start installing fluent~")
        install_fluent_cmd="/root/local/bin/kubectl create -f " + basedir +"/Yaml/fluentd-es-configmap.yaml \n" \
        + "/root/local/bin/kubectl create -f " +basedir+ "/Yaml/fluentd-es-ds-temp.yaml" 
        install_doc=os.popen(install_fluent_cmd).read().strip()
        logging.info(install_doc)

        logger.info("Success, Installed fluent complete")


if __name__=="__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--install":
        install_fluent()
    elif len(sys.argv) == 2 and sys.argv[1] == "--delete":
        delete_fluent_cluster()
    elif len(sys.argv) == 2 and sys.argv[1] == "--check":
    	check_fluent_health()
    elif len(sys.argv) == 2 and sys.argv[1] == "--expand":
    	expand_fluent()
    else:
        print(
            "--install (install fluent cluster) \n"
            "--delete (delete fluent cluster) \n"
            "--check (check fluent cluster health) \n"
            "--expand (expand fluent cluster)"
        )


    
