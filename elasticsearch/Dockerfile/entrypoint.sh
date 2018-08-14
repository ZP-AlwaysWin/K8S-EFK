#!/bin/bash

#set -e

# Add elasticsearch as command if needed
#if [ "${1:0:1}" = '-' ]; then
#        set -- elasticsearch "$@"
#fi

set -- elasticsearch "$@"
echo "$@"
# Drop root privileges if we are running elasticsearch
# allow the container to be started with `--user`
if [ "$1" = 'elasticsearch' -a "$(id -u)" = '0' ]; then
        # Change the ownership of user-mutable directories to elasticsearch
        for path in \
               /usr/share/elasticsearch/data \
               /usr/share/elasticsearch/logs \
        ; do
                chown -R elasticsearch:elasticsearch "$path"
        done

        set -- gosu elasticsearch "$@"
        #exec gosu elasticsearch "$BASH_SOURCE" "$@"
fi

if [ -z $MY_POD_NAME ]; then
    echo "ERROR: You should specify MY_POD_NAME."
    exit 1
fi

if [ -z $MY_POD_IP ]; then
    echo "ERROR: You should specify MY_POD_IP."
    exit 1
fi

sleep 10

cp /home/elasticsearch/config/* /usr/share/elasticsearch/config/

echo "MY_POD_NAME"
echo $MY_POD_NAME
echo "sed 1:"
cat /usr/share/elasticsearch/config/elasticsearch.yml


sed -i s/"NODE_NAME"/$MY_POD_NAME/g /usr/share/elasticsearch/config/elasticsearch.yml

echo "sed 2:"
cat /usr/share/elasticsearch/config/elasticsearch.yml

sed -i s/"0.0.0.0"/$MY_POD_IP/g /usr/share/elasticsearch/config/elasticsearch.yml
#sysctl -w vm.max_map_count=655360

# As argument is not related to elasticsearch,
# then assume that user wants to run his own process,
# for example a `bash` shell to explore this image
echo "Ready to start......."

exec "$@"
