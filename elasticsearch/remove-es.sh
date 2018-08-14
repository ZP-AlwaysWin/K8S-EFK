#!/bin/bash

/root/local/bin/kubectl delete sts elasticsearch --namespace=kube-efk
/root/local/bin/kubectl delete svc elasticsearch --namespace=kube-efk
/root/local/bin/kubectl delete configmap es-configmap --namespace=kube-efk

for i in `/root/local/bin/kubectl get node|grep -v NAME|awk '{print $1}'`;
do
    /root/local/bin/kubectl label node $i es- >/dev/null 2>&1
done

po_list=$(/root/local/bin/kubectl get sts --namespace=kube-efk | grep elasticsearch)
if [ -z $po_list ]; then
    pvc_list=$(/root/local/bin/kubectl get pvc --namespace=kube-efk | grep elasticsearch | awk '{print $1}')
    for pvc in $pvc_list ;
    do
        /root/local/bin/kubectl delete pvc $pvc --namespace=kube-efk
    done
else
    exit 1
fi

svc_num=1
ep_num=1
wait_time=0
while [ $svc_num -ne 0 -o $ep_num -ne 0 ]&&[ $wait_time < 60 ]; do
    sleep 5
    ep_num=$(/root/local/bin/kubectl get endpoints | grep dynamic-es | wc -l)
    svc_num=$(/root/local/bin/kubectl get service | grep dynamic-es | wc -l)
    let wait_time=$wait_time+1
done

if [ $wait_time -ge 60 ]; then
    exit 1
fi
