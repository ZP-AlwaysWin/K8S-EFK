#encoding=utf-8

import json
import os           
import re
import logging
import sys
import time
from   ConfigParser import *
import fluent.Install_fluent as fluent 
import elasticsearch.elasticsearch as ela
import kibana.kibana as kibana
import elasticsearch.check as ela_health
import elasticsearch.utils as check_ela

basedir=os.path.split(os.path.realpath(__file__))[0]

logger = logging.getLogger("Install-All-EFK")

formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')

Install_log_path=basedir+"/log/Install-All-EFK.log"
file_handler = logging.FileHandler(Install_log_path)
file_handler.setFormatter(formatter) 

console_handler = logging.StreamHandler(sys.stdout)
console_handler.formatter = formatter  

logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.setLevel(logging.INFO)

ini_path=basedir+"/EFK-config.ini"
config=SafeConfigParser()
config.read(ini_path)

create_n_cmd="/root/local/bin/kubectl apply -f "+basedir+"/yaml/kube-efk-namespace.yaml >/dev/null 2>&1"
exist_n_cmd="/root/local/bin/kubectl get namespace kube-efk >/dev/null 2>&1"
compile_ip = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')



def read_file (filename):
    f = open(filename)
    content = f.read()
    f.close()
    return content

def write_file (filename, text):
    f = open(filename, 'w')
    f.write(text)
    f.close()


def createSecretOfCeph():
    logger.info('Create secret ceph-secret for kube-efk namespace')
    replace_cmd = 'my_tmp_key=`ceph auth get-key client.admin --cluster ceph-k8s | base64` && sed -i "s#key:.*#key: $my_tmp_key#g"' + ' ' + basedir + '/yaml/kube-efk-namespace.yaml'
    return_r_cmd=os.system(replace_cmd)
    if return_r_cmd:
        logger.error("Replace kube-efk namespace ceph-secret failure")
        return 1
    else:
        logger.info("Replace kube-efk namespace ceph-secret success")


def create_namespace():
    return_exist_n=os.system(exist_n_cmd)
    if return_exist_n:
        return_n_code=createSecretOfCeph()
        if return_n_code:
	        return 1
        else:
            logger.info("Starting creating kub-efk namespaces")
            return_n_cmd=os.system(create_n_cmd)
            if return_n_cmd:
                logger.error("Creating kube-efk namespace failure")
                return 1
            else:
                logger.info("Creating kube-efk namespace success")
    else:
        logger.error("Kubernetes Cluster exists EFK namespace, Please do not repeat the installation")
        return 1

def check_config():
    return_exist_n=os.system(exist_n_cmd)
    if return_exist_n:
        pass
    else:
        logger.error("Kubernetes Cluster exists EFK namespace, Please do not repeat the installation")
        return 1

    try:
       # wait_kibana_time=config.get("Kibana","wait_kibana_time")
       # if int(wait_kibana_time) <=0:
       #     logger.error("Kibana install wait time must be more than 0")
       #     return 1
        fluent_node = config.get("Fluent", "fluent_node")
        wait_fluent_time=config.get("Fluent","wait_fluent_time")

        if int(wait_fluent_time) <=0:
            logger.error("Fluent install wait time must be more than 0")
            return 1
        if len(fluent_node.strip()):
            list_temp_ip=fluent_node.split(",")
            for ip in list_temp_ip:
                if compile_ip.match(ip.strip()):
                    pass
                else:
                    logger.error("Fluent Node iP is illegal ")
                    return 1
        else:
            logger.error("The fluent node ip is empty")
            return 1

        ela_node = config.get("Elasticsearch", "node_ips")
        ifhostmouth = config.get("Elasticsearch","hostPath")
        size= config.get("Elasticsearch","size")
        wait_elasticsearch_time = config.get("Elasticsearch","wait_elasticsearch_time")
        pathDir = config.get("Elasticsearch","pathDir")
        if int(wait_elasticsearch_time) <=0:
            logger.error("Elasticsearch install wait time must be more than 0")
            return 1
        if len(ela_node.strip()):
            list_temp_ip=ela_node.split(",")
            for ip in list_temp_ip:
                if compile_ip.match(ip.strip()):
                    pass
                else:
                    logger.error("Elasticsearch Node iP is illegal")
                    return 1
        else:
            logger.error("The elasticsearch node ip is empty")
            return 1

        if str(ifhostmouth) !="true" and str(ifhostmouth) !="false":
            logger.error("Elasticsearch storage Whether or not to mount to the host is not clear")
            return 1

        if int(size) <=0:
            logger.error("Elasticsearch storage size must be more than 0")
            return 1

    except NoOptionError as e:
        logger.error(e)
        return 1
    except NoSectionError as e:
        logger.error(e)
        return 1
    except ValueError as e:
        logger.error(e)
        return 1
    except Exception as e:
        logger.error(e)
        return 1

    try:
        ela_node = config.get("Elasticsearch", "node_ips")
        ifhostmouth = config.get("Elasticsearch","hostPath")
        hostDir=config.get("Elasticsearch","pathDir")
        size= config.get("Elasticsearch","size")
        wait_elasticsearch_time = config.get("Elasticsearch","wait_elasticsearch_time")
        if int(wait_elasticsearch_time) <=0:
            logger.error("Elasticsearch install wait time must be more than 0")
            return 1
        list_temp_ip=ela_node.split(",")
        list_ip=[]
        for ip in list_temp_ip:
            if compile_ip.match(ip.strip()):
                list_ip.append(ip.strip())
            else:
                logger.error("Elasticsearch Node iP is illegal")
                return 1
        
        if str(ifhostmouth) !="true" and str(ifhostmouth) !="false":
            logger.error("Elasticsearch storage Whether or not to mount to the host is not clear")
            return 1
        
        if int(size) <=0:
            logger.error("Elasticsearch storage size must be more than 0")
            return 1

        test={}
        test['storage']={"hostPath":ifhostmouth,"pathDir":hostDir,"size":size}
        test['scale']={"new_ips":[]}
        test['elasticsearch']={"node_ips":list_ip}

        elasticsearch_config_path=basedir+"/elasticsearch/config/es.json"
        fb = open(elasticsearch_config_path,'w')
        fb.write(json.dumps(test,indent=2))
        fb.close()
    except ValueError as e:
        logger.error(e)
        return 1
    except NoOptionError as e:
        logger.error(e)
        return 1
    except NoSectionError as e:
        logger.error(e)
        return 1
    except Exception as e:
        logger.error("Obtaining Elasticsearch information occur unknown error")
        logger.error(e)
        return 1
    
    if check_ela.check_install(elasticsearch_config_path):
        logger.error("checking Elasticsearch config occur error")
        return 1

    try:
        fluent_node = config.get("Fluent", "fluent_node")
        wait_fluent_time=config.get("Fluent","wait_fluent_time")
        
        if int(wait_fluent_time) <=0:
            logger.error("Fluent install wait time must be more than 0")
            return 1
        if len(fluent_node):
            data={}
            list_temp_ip=fluent_node.split(",")
            list_ip=[]
            for ip in list_temp_ip:
                if compile_ip.match(ip.strip()):
                    list_ip.append(ip.strip())
                else:
                    logger.error("Fluent Node iP is illegal ")
                    return 1
            data['fluent_node'] = list_ip
            fluent_config_path=basedir+"/fluent/fluent.json"
            fb = open(fluent_config_path,'w')
            fb.write(json.dumps(data,indent=2))
            fb.close()
        else:
            logger.error("The fluent node ip is empty")
            return 1
    except NoOptionError as e:
        logger.error("EFK config don't have fluent node ip")
        logger.error(e)
        return 1
    except NoSectionError as e:
        logger.error(e)
        return 1
    except ValueError as e:
        logger.error(e)
        return 1
    except Exception as e:
        logger.error("Obtaining fluent node ip occur unknown error")
        logger.error(e)
        return 1

    return_code=fluent.get_config(fluent_config_path)

    if isinstance(return_code,int):
        logger.error("checking Fluent config occur error")
        return 1





def install_elasticsearch():
    
    logger.info("Starting installing elasticsearch cluster")
    wait_elasticsearch_time = config.get("Elasticsearch","wait_elasticsearch_time")
    return_elasticsearch=ela.install_elasticsearch()
    if return_elasticsearch:
        logger.error("Installing elasticsearch cluster failure")
        return 1
    else:
        logger.info("Installing elasticsearch cluster success")
    
    logger.info("Starting checking elasticsearch cluster health")
    count=0
    while count<int(wait_elasticsearch_time):
        time.sleep(60)
        return_elasticsearch_health=ela_health.check_cluster()
        if return_elasticsearch_health:
            count=count+1
        else:
            logger.info("Elasticsearch cluster already in a state of health")
            return 0
    logger.error("Elasticsearch cluster after {} minutes still in a state of crash, Jump out of the installation, please retest".format(wait_elasticsearch_time))
    return 1    

def install_fluent():

    logger.info("Starting installing fluent cluster")
    wait_fluent_time=config.get("Fluent","wait_fluent_time")
    return_fluent=fluent.install_fluent()
    if return_fluent:
        logger.error("Installing fluent cluster failure")
        return 1
    else:
        logger.info("Installing fluent cluster success")
    
    logger.info("Starting checking fluent cluster health")
    count=0
    while count<int(wait_fluent_time):
        time.sleep(60)
        return_fluent_health=fluent.check_fluent_health()
        if return_fluent_health:
            count=count+1
        else:
            logger.info("Fluent cluster already in a state of health")
            return 0
    logger.error("Fluent cluster after {} minutes still in a state of crash, Jump out of the installation, please retest".format(wait_fluent_time))
    return 1

def install_kibana_with_check():
    logger.info("Starting installing Kibana ")
    try:
        wait_kibana_time=config.get("Kibana","wait_kibana_time")
        if int(wait_kibana_time) <=0:
            logger.error("Kibana install wait time must be more than 0")
            return 1
        kibana.install()
    except NoOptionError as e:
        logger.error(e)
        return 1
    except NoSectionError as e:
        logger.error(e)
        return 1
    except ValueError as e:
        logger.error(e)
        return 1
    except Exception as e:
        logger.error(e)
        logger.error("Installing kibana failure")
        return 1

    logger.info("Installing kibana success")

    logger.info("Starting checking kibana health")
    logger.info("It takes about 10 minutes,Please be patient")
    logger.info("At present, the maximum test time is {} minutes".format(wait_kibana_time))
    logger.info("If {} minutes are still not successful, please check the performance of the machine.".format(wait_kibana_time))
    count=0
    while count<int(wait_kibana_time):
        time.sleep(60)
        return_kibana_health=kibana.check()
        if return_kibana_health:
            count=count+1
        else:
            logger.info("Kibana already in a state of health")
            return 0
    logger.error("Kibana after {} minutes still in a state of crash, Jump out of the installation, please retest".format(wait_kibana_time))
    return 1

def install_kibana():
    logger.info("Starting installing Kibana ")
    try:
        kibana.install()
    except Exception as e:
        logger.error(e)
        logger.error("Installing kibana failure")
        return 1
    logger.info("Installing kibana success")
    logger.info("Kibana component is not automatically detected, it will take about 15 minutes to initialize successfully.")
    logger.info("Please call the script yourself to see if the EFK cluster is successful.")
    logger.info("eg: python -m scripts.EFK.AllCheck")

def install_efk():
    logger.info("Starting install all EFK ")
    return_config=check_config()
    if return_config:
        logger.error("Install EFK config is illegal")
        return 1
    else:
        return_name=create_namespace()
    if return_name:
        logger.error("Install EFK failure,Please check the unload retry")
        return 1
    else:
        return_elasticsearch=install_elasticsearch()

    if return_elasticsearch:
        logger.error("Install EFK failure,Please check the unload retry")
        return 1
    else:
        return_fluent=install_fluent()

    if return_fluent:
        logger.error("Install EFK failure,Please check the unload retry")
        return 1
    else:
        return_kibana=install_kibana()
    
    if return_kibana:
        logger.error("Install EFK failure,Please check the unload retry")
        return 1
    else:
        logger.info("Congratulate,Install all EFK success")

if __name__=="__main__":
    install_efk()
