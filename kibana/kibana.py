# -*- coding: utf-8 -*-
import subprocess
import os
import sys

# base directory of current script
basedir = os.path.split(os.path.realpath(__file__))[0]

def call_shell(cmd = "echo ok", exit_on_error = False):
    shell = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    shell.wait()
    result = {'code': shell.returncode, 'out': shell.stdout.read()}
    if result['code'] != 0 and exit_on_error == True :
        raise Exception('command terminated with code ' + str(code))
    return result

def install():
    call_shell("/root/local/bin/kubectl -n kube-efk create -f {}/kibana-svc.yaml".format(basedir), True)
    call_shell("/root/local/bin/kubectl -n kube-efk create configmap kibana-configmap --from-file={}/kibana-conf/".format(basedir), True)
    call_shell("/root/local/bin/kubectl -n kube-efk create -f {}/kibana-dep.yaml".format(basedir), True)

def uninstall():
    code = 0
    result = call_shell("/root/local/bin/kubectl -n kube-efk delete deployment kibana")
    code += result['code']
    result = call_shell("/root/local/bin/kubectl -n kube-efk delete configmap kibana-configmap")
    code += result['code']
    result = call_shell("/root/local/bin/kubectl -n kube-efk delete svc kibana")
    code += result['code']
    return code

def check():
    # service exists ?
    result = call_shell("/root/local/bin/kubectl -n kube-efk get svc kibana --no-headers")
    if result['code'] != 0:
        return 1

    # ready == expected ?
    result = call_shell("/root/local/bin/kubectl -n kube-efk get deployment kibana -o=jsonpath='{.spec.replicas}'")
    if result['code'] != 0:
        return 1
    expected = result['out'].strip()
    result = call_shell("/root/local/bin/kubectl -n kube-efk get deployment kibana -o=jsonpath='{.status.readyReplicas}'")
    if result['code'] != 0:
        return 1
    ready = result['out'].strip()
    if expected != ready :
        print('[WARN] ready replicas({}) is not equal to expected replicas({})'.format(ready, expected))
        return 2
    # running pods == expected ?
    result = call_shell("/root/local/bin/kubectl -n kube-efk get pod -l k8s-app=kibana --no-headers | grep -c Running")
    if result['code'] != 0 :
        return 1
    running = result['out'].strip()
    if expected != running :
        print('[WARN] running replicas({}) is not equal to expected replicas({})'.format(running, expected))
        return 1
    # http request to port 5601
    result = call_shell("/root/local/bin/kubectl -n kube-efk get pod -l k8s-app=kibana --no-headers -o wide 2>/dev/null | awk '{print $6}' | xargs echo")
    pods = result['out'].split()
    result = call_shell("/root/local/bin/kubectl get service kibana -n kube-efk -o jsonpath='{.spec.clusterIP}'")
    pods.append(result['out'])
    for i in range(len(pods)) :
        result = call_shell('curl -m 10 -s http://{}:5601/'.format(pods[i]))
        if result['code'] != 0:
            print('[WARN] failed to access http://{}:5601/'.format(pods[i]))
            return 4
    
    return 0

if __name__ == "__main__" :
    if len(sys.argv) < 2 :
        print("usage: python kibana.py install|uninstall|check")
        sys.exit(1)
    command = sys.argv[1]
    if "check" == command :
        if check() == 0 :
            print("Kibana is ready ~")
        else :
            print('kibana is not ready.')
    elif "install" == command :
        install()
        print("Kibana is installed.")
    elif "uninstall" == command :
        uninstall()
        print('done!')
    else :
        print("[ERROR] unknow option.")
        print("usage: python kibana.py install|uninstall|check")
