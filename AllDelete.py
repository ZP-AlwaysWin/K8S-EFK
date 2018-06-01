#encoding=utf-8

import json
import os           
import shutil
import math
import re
import logging
import sys
import time
from ConfigParser import *
import fluent.Install_fluent as fluent 
import elasticsearch.elasticsearch as ela
import kibana.kibana as kibana
import elasticsearch.check as ela_health
import elasticsearch.remove_es as re_es

basedir=os.path.split(os.path.realpath(__file__))[0]

logger = logging.getLogger("Delete-All-EFK")

formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')

delete_log_path=basedir+"/log/Delete-All-EFK.log"
file_handler = logging.FileHandler(delete_log_path)
file_handler.setFormatter(formatter) 

console_handler = logging.StreamHandler(sys.stdout)
console_handler.formatter = formatter  

logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.setLevel(logging.INFO)

exist_n_cmd="/root/local/bin/kubectl get namespace kube-efk >/dev/null 2>&1"
delete_n_cmd="/root/local/bin/kubectl delete namespace kube-efk >/dev/null 2>&1"

def exists_namespace():
    return_exist_n=os.system(exist_n_cmd)
    if return_exist_n:
        logger.error("Kubernetes Cluster Non-existent EFK, Please do not repeat the deletion")
    else:
        return 1

def delete_fluent():
    return_fluent=fluent.delete_fluent_cluster()
    time.sleep(10)
    if return_fluent:
        logger.error("Delete fluent cluster failure")
        return 1


def delete_elasticsearch():
    logger.info("Start deleting elasticsearch cluster")
    return_elasticsearch=re_es.remove_cluster()
    time.sleep(10)
    if return_elasticsearch:
        logger.error("Delete elasticsearch cluster failure")
        return 1
    else:
        logger.info("Delete elasticsearch cluster success")

def delete_kibana():
    logger.info("Start deleting Kibana")
    return_kibana=kibana.uninstall()
    time.sleep(6)
    if return_kibana:
        logger.error("Delete Kibana occur unknown error")
        return 1
    else:
        logger.info("Delete Kibana success")

def delete_namespaces():
    return_delete_n=os.system(delete_n_cmd)
    time.sleep(10)
    if return_delete_n:
        logger.error("Delete namespace kube-efk failure")
        return 1
    else:
        logger.info("Delete namespace kube-efk success")

etcd_get_cmd="export ETCDCTL_API=3 \n" \
	+ "etcdctl get /registry --prefix --keys-only|grep kube-efk"

def etcd_delete():
    return_etcd=os.popen(etcd_get_cmd).read().strip()
    if return_etcd:
        return_list=return_etcd.split("\n")
        for i in return_list:
            print(i)
            etcd_del_cmd="etcdctl del "+i.strip()
            os.system(etcd_del_cmd)
    else:
        logger.info("Etcd cluster Non-existent kube-efk")

def delete_all_efk():
    return_n=exists_namespace()
    if return_n:
        return_elasticsearch=delete_elasticsearch()
        return_fluent=delete_fluent()
        return_kibana=delete_kibana()
        delete_namespaces()
    else:
        return 1
   
    time.sleep(60)
    etcd_delete()

    while os.popen(etcd_get_cmd).read().strip():
        etcd_delete()
    else:
        logger.info("Deleting EFK cluster success")



if __name__=="__main__":
    logger.info("Starting deleting EFK cluster")
    delete_all_efk()

