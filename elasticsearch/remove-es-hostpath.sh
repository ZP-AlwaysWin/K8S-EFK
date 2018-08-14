#!/bin/bash

host_path=$1

node_IPs=$(/root/local/bin/kubectl get po -o wide --namespace=kube-efk | grep elasticsearch | awk '{print $7}')

/root/local/bin/kubectl delete sts elasticsearch --namespace=kube-efk
/root/local/bin/kubectl delete svc elasticsearch --namespace=kube-efk
/root/local/bin/kubectl delete configmap es-configmap --namespace=kube-efk

for i in `/root/local/bin/kubectl get node|grep -v NAME|awk '{print $1}'`;
do
    /root/local/bin/kubectl label node $i es- >/dev/null 2>&1
done

for node_IP in $node_IPs ;
do
    ssh $node_IP "rm -rf $host_path/data"
    ssh $node_IP "rm -rf $host_path/logs"
done
