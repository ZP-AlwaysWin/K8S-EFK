import os

res=os.popen("curl -s -uelastic:changeme http://172.20.0.12:9200/_cat/health?pretty | awk '{print $4}' >/dev/null 2>&1").readlines()

print(res)
