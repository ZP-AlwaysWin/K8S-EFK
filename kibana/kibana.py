# -*- coding: utf-8 -*-
import subprocess
import os
import sys

# base directory of current script
basedir = os.path.split(os.path.realpath(__file__))[0]

def call_shell(cmd = "echo ok", exit_on_error = False):
    shell = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    shell.wait()
    code = shell.returncode
    result = {'code': code}
    result['out'] = shell.stdout.read()
    result['err'] = shell.stderr.read()
    if code != 0:
        if exit_on_error == True :
            print('[ERROR]: return code is {}. {}'.format(code, result['err']))
            raise Exception('command terminated with code ' + str(code))
        else:
            print('[WARN]: return code is {}. {}'.format(code, result['err']))
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
    call_shell("/root/local/bin/kubectl -n kube-efk get svc kibana --no-headers", True)
    # ready == expected ?
    result = call_shell("/root/local/bin/kubectl -n kube-efk get deployment kibana -o=jsonpath='{.spec.replicas}'", True)
    expected = result['out']
    result = call_shell("/root/local/bin/kubectl -n kube-efk get deployment kibana -o=jsonpath='{.status.readyReplicas}'", True)
    ready = result['out']
    if expected != ready :
        return 1
    # running pods == expected ?
    result = call_shell("/root/local/bin/kubectl -n kube-efk get pod -l k8s-app=kibana --no-headers | grep -c Running")
    if result['code'] == 0 :
        if expected != result['out'].strip() :
            return 2
    else :
        return 3
    # http request to port 5601
    result = call_shell("/root/local/bin/kubectl -n kube-efk get pod -l k8s-app=kibana --no-headers -o wide 2>/dev/null | awk '{print $6}' | xargs echo")
    pods = result['out'].split()
    for i in range(len(pods)) :
        result = call_shell('curl -m 5 http://{}:5601/'.format(pods[i]))
        if result['code'] != 0:
            return 4
    return 0

if __name__ == "__main__" :
    if len(sys.argv) < 2 :
        print("usage: python kibana.py install|uninstall|check")
        sys.exit(1)
    command = sys.argv[1]
    if "check" == command :
        code=check()
        if code == 0 :
            print("Kibana is ready ~")
        else :
            print(code)
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
