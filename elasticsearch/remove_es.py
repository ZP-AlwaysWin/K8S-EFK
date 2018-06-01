import os
import sys
import subprocess
from ...k8s.volumes import delete_volumes

dir=os.path.split(os.path.realpath(__file__))[0]

def remove_cluster():
    os.system("chmod +x " + dir + "/remove-es.sh")
    pvc_list = os.popen("/root/local/bin/kubectl get pvc --namespace=kube-efk | grep elasticsearch | awk '{print $3}'").readlines()
    arg=""
    try:
        if(sys.argv[1]=="stop"):
            print("Keep data")
            arg="stop"
    except:
        print("Remove all")
    vol_list = []
    for pvc in pvc_list:
        pvc = pvc.replace("\n", "")
        vol=os.popen("/root/local/bin/kubectl get pv " + pvc + " --namespace=kube-efk -o=jsonpath='{.spec.glusterfs.path}'").readlines()[0]
        vol_list.append(vol)
    print(vol_list)
    remove_result = call_shell("sh " + dir + "/remove-es.sh ")
    print("Message: " + str(remove_result["message"]))
    print("Remove_result is " + str(remove_result["code"]))
    if remove_result["code"] == 0:
        delete_volumes(vol_list)
        return 0
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

if __name__ == '__main__':
    try:
        remove_cluster()
    except:
        print("except")
