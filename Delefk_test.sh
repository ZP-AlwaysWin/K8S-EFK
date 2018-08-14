#!/bin/bash
while true; do
        for e in `kubectl get pod -n kube-efk|awk '/elasticsearch/{print $1}'`;
		do
		      kubectl delete pod $e  -n kube-efk
		done
        sleep 60
		
        for i in `kubectl get pod -n kube-efk|awk '/fluent/{print $1}'`;
        do
              kubectl delete pod $i -n kube-efk
        done
        sleep 120
done

