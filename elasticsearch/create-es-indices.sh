#!/bin/bash

for i in `seq 30`;
do
    date_time=$(date -d "$i day ago" +%Y.%m.%d)
    index_name="logstash-"$date_time
    curl -s -X PUT "http://172.20.0.157:9200/$index_name"
done
