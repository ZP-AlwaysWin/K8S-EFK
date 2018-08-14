#!/bin/bash

days=$1
if [ -z $days ]; then
    echo "No days"
    exit 1
fi

if [ $days -le 0 ]; then
   echo "The number must be larger than 0"
   exit 1
fi

let days=$days-1

echo '#!/bin/sh

year=$(date +%Y)
elasticsearch_address=$(/bin/kubectl --server="$K8S_HOST:$K8S_PORT" get po -o wide -n kube-efk | grep elasticsearch-0 | awk '"'"'{print $7}'"'"')

echo $elasticsearch_address
for i in `seq 10`;
do
    let j=$i+'"$days"'
    date_time=$(date -d "$j day ago" +%Y.%m.%d)
    index_name="logstash-"$date_time
    curl -X DELETE "http://$elasticsearch_address:9200/$index_name" > /dev/null 2>&1
    echo $index_name
done' > ../../k8s/ansible/roles/logrotate/files/elasticsearch-clean.sh

/root/local/bin/kubectl delete configmap logrotate-configmap
/root/local/bin/kubectl create configmap logrotate-configmap --from-file=../../k8s/ansible/roles/logrotate/files/

