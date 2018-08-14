import os
import sys
import time
import utils
import subprocess

dir=os.path.split(os.path.realpath(__file__))[0]
config_path = "/config/es.json"

def remove_cluster():
    data = utils.get_conf(dir + config_path)
    host_bl = data["storage"]["hostPath"]
    host_path = data["storage"]["pathDir"]
    os.system("chmod +x " + dir + "/remove-es.sh")
    pvc_list = os.popen("/root/local/bin/kubectl get pvc --namespace=kube-efk | grep elasticsearch | awk '{print $3}'").readlines()
    arg=""
    try:
        if(sys.argv[1]=="stop"):
            print("Keep data")
            arg="stop"
    except:
        print("Remove all")
    if host_bl == "true":
        print("hostPath: " + str(host_path))
        remove_result = call_shell("sh " + dir + "/remove-es-hostpath.sh " + str(host_path))
    else:
        remove_result = call_shell("sh " + dir + "/remove-es.sh " + str(host_path))
    print("Message: " + str(remove_result["message"]))
    print("Remove_result is " + str(remove_result["code"]))
    if remove_result["code"] == 0:
        print("Remove es successfully!")
        return 0
    print("Failed to remove es")
    return 1

def call_shell(cmd):
    shell = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    shell.wait()
    code = shell.returncode
    result = {'code': code}
    if code == 0:
        result['message'] = shell.stdout.read()
    else:
        result['message'] = shell.stdout.read()
    return result

def remove_es_cluster():
    wait_times = 0
    remove_result = 1
    while (wait_times < 10 and remove_result == 1):
        try:
            remove_result = remove_cluster()
            if remove_result == 0:
                return 0
        except:
            remove_result = 1
        time.sleep(10)
    return 1

if __name__ == '__main__':
    try:
        remove_cluster()
    except Exception, e:
        print(Exception, "   ", e)
