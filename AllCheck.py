#encoding=utf-8

import json
import os           
import math
import re
import logging
import sys
import time
import fluent.Install_fluent as fluent 
import kibana.kibana as kibana
import elasticsearch.check as ela_health


basedir=os.path.split(os.path.realpath(__file__))[0]

logger = logging.getLogger("Check-All-EFK")

formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')

check_log_path=basedir+"/log/Check-All-EFK.log"
file_handler = logging.FileHandler(check_log_path)
file_handler.setFormatter(formatter) 

console_handler = logging.StreamHandler(sys.stdout)
console_handler.formatter = formatter  

logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.setLevel(logging.INFO)

exist_n_cmd="/root/local/bin/kubectl get namespace kube-efk >/dev/null 2>&1"

def check_namespaces():
    return_namespace=os.system(exist_n_cmd)
    if return_namespace:
        logger.error("Kubernetes Cluster don't exist kube-efk namespace")
        return 1

def check_fluent():
    logger.info("Starting checking fluent cluster health")
    return_fluent_health=fluent.check_fluent_health()
    if return_fluent_health:
        logger.error("Fluent cluster not in a state of health")
        return 1
    else:
        logger.info("Fluent cluster already in a state of health")
    

def check_elasticsearch():
    logger.info("Starting checking elasticsearch cluster health")
    return_elasticsearch_health=ela_health.check_cluster()
    if return_elasticsearch_health:
        logger.error("Elasticsearch cluster not in a state of health")
        return 1 
    else:
        logger.info("Elasticsearch cluster already in a state of health")
          

def check_kibana():
    logger.info("Starting checking kibana health")
    return_kibana_health=kibana.check()
    if return_kibana_health:
        logger.error("Kibana cluster not in a state of health")
        return 1
    else:
        logger.info("Kibana already in a state of health")

    
def check_all_efk():
    logger.info("Starting checking all EFK health")
    return_na=check_namespaces()
    if return_na:
        logger.error("All EFK cluster not in a state of health")
        return 1
    else:
        return_fluent=check_fluent()
    if return_fluent:
        logger.error("All EFK cluster not in a state of health")
        return 1
    else:
        return_elasticsearch=check_elasticsearch()

    if return_elasticsearch:
        logger.error("All EFK cluster not in a state of health")
        return 1
    else:
        return_kibana=check_kibana()
    
    if return_kibana:
        logger.error("All EFK cluster not in a state of health")
        return 1
    else:
        logger.info("All EFK cluster already in a state of health")

if __name__=="__main__":
    check_all_efk()    
